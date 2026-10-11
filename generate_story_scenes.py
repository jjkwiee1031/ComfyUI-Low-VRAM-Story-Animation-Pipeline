import json, os, subprocess, time
from PIL import Image, ImageDraw, ImageFont

asset_dir = "/home/jjk-wsl/comfyui/story-to-handdrawn-video/public/assets/generated/codex/手绘故事-0e0bb52e"
os.makedirs(asset_dir, exist_ok=True)

tasks = [
  ("00_character_reference.png", "cute orange tabby cat character sheet, front view and 3/4 view, wearing white astronaut suit, colored pencil drawing, white background, simple lines", "主角设定：宇航猫猫"),
  ("01_master.png", "a cute cat wearing a white astronaut suit, helmet, colored pencil sketch, storybook illustration, white background, simple outline", "小猫穿上了宇航服。"),
  ("02_master.png", "a cute cat astronaut boarding a retro space rocket, ladder, launching pad, colored pencil drawing, children book art, white background", "它登上了飞往火星的飞船。"),
  ("03_master.png", "a cute cat astronaut on red Mars planet, small paw print on red dust, earth in sky, colored pencil drawing, storybook illustration, white background", "在红色星球上留下了第一只猫爪印。")
]

workflow_template_path = "/home/jjk-wsl/comfyui/workflows/sd15_hypersd_api.json"
temp_workflow = "/home/jjk-wsl/comfyui/workflows/temp_run.json"
output_dir = "/home/jjk-wsl/comfyui/ComfyUI/output"

with open(workflow_template_path, "r") as f:
    base_wf = json.load(f)

for filename, prompt, caption in tasks:
    print(f"\n==========================================")
    print(f"Generating scene with ComfyUI: {filename}")
    print(f"Prompt: {prompt}")
    print(f"==========================================")
    
    before_files = set(os.listdir(output_dir))
    
    # Update prompt and prefix in temp json
    tag = filename.replace(".png", "")
    prefix = f"Story_{tag}"
    base_wf["3"]["inputs"]["text"] = prompt
    base_wf["8"]["inputs"]["filename_prefix"] = prefix
    
    # Randomize seed for new images
    import random
    base_wf["6"]["inputs"]["seed"] = random.randint(100000, 99999999)
    
    with open(temp_workflow, "w") as f:
        json.dump(base_wf, f, indent=2)
        
    cmd = ["comfy", "run", "--workflow", temp_workflow, "--wait", "--timeout", "300"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("Comfy run stdout:", res.stdout)
        print("Comfy run stderr:", res.stderr)
        raise RuntimeError(f"ComfyUI run failed for {filename}")
        
    time.sleep(1)
    after_files = set(os.listdir(output_dir))
    new_files = [f for f in (after_files - before_files) if f.startswith(prefix)]
    if not new_files:
        candidates = sorted([f for f in os.listdir(output_dir) if f.startswith(prefix)], key=lambda x: os.path.getmtime(os.path.join(output_dir, x)))
        new_file = candidates[-1]
    else:
        new_file = new_files[0]
        
    src_path = os.path.join(output_dir, new_file)
    dst_path = os.path.join(asset_dir, filename)
    print(f"✓ Generated raw image from ComfyUI: {src_path}")
    
    # Resize and place onto the story master canvas (1024x1536)
    gen_img = Image.open(src_path).convert("RGB")
    gen_img = gen_img.resize((860, 860), Image.Resampling.LANCZOS)
    
    master_canvas = Image.new("RGB", (1024, 1536), color=(255, 255, 255))
    master_canvas.paste(gen_img, (82, 580))
    
    draw = ImageDraw.Draw(master_canvas)
    cjk_font_path = os.path.expanduser("~/.local/share/fonts/NotoSansSC-Regular.otf")
    try:
        font = ImageFont.truetype(cjk_font_path, 38)
    except Exception:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 38)
        except Exception:
            font = ImageFont.load_default()
    draw.text((80, 140), caption, fill=(30, 30, 30), font=font)
    
    master_canvas.save(dst_path)
    print(f"✓ Master plate saved to: {dst_path}")

print("\nAll ComfyUI scenes generated successfully!")
