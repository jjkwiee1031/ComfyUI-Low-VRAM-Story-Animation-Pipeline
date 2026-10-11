import json, os, time, urllib.request, random
from PIL import Image, ImageDraw, ImageFont

with open("/home/jjk-wsl/comfyui/story-to-handdrawn-video/codex-image-jobs.json", "r") as f:
    manifest = json.load(f)

ASSET_DIR = f"/home/jjk-wsl/comfyui/story-to-handdrawn-video/public/assets/generated/codex/{manifest['asset_set']}"
OUTPUT_DIR = "/home/jjk-wsl/comfyui/ComfyUI/output"
TEMPLATE_PATH = "/home/jjk-wsl/comfyui/workflows/sd15_coolkids_api.json"
FONT_PATH = os.path.expanduser("~/.local/share/fonts/NotoSansSC-Regular.otf")

os.makedirs(ASSET_DIR, exist_ok=True)

# Minimalist line explainer style prompts
style_positive = "minimalist black and white line art, clean technical doodle, naive felt pen outline, stick figure, white background, simple clean drawing, no color, no gradients, no shading"
style_negative = "blurry, low quality, distorted, bad anatomy, photorealistic, 3d, complex texture, color, gradient, shading, hatching, solid black fill"

tasks = [
  ("00_character_reference.png", f"a cute little rusty robot character reference, front view and 3/4 view, minimalist black line drawing, {style_positive}", "主角设定：小机器人"),
  ("01_master.png", f"a cute little rusty robot walking peacefully in a sparse quiet field, minimalist black line drawing, {style_positive}", "锈迹斑斑的小机器人漫步在寂静草地。"),
  ("02_master.png", f"a cute little robot bending down and picking up a tiny glowing fallen star in grass, minimalist black line drawing, {style_positive}", "它在草丛中捡起了一颗掉落的微光小星星。"),
  ("03_master.png", f"a cute little robot throwing a tiny star high up into the night sky with effort, minimalist black line drawing, {style_positive}", "它用尽全力把星星重新抛回夜空。"),
  ("04_master.png", f"night sky shining bright with stars, cute little robot smiling and waving hand, minimalist black line drawing, {style_positive}", "夜空再次亮起，小机器人微笑挥手。")
]

with open(TEMPLATE_PATH, "r") as f:
    base_wf = json.load(f)

base_wf["4"]["inputs"]["text"] = style_negative

def queue_prompt(prompt_wf):
    p = {"prompt": prompt_wf}
    data = json.dumps(p).encode('utf-8')
    req = urllib.request.Request("http://127.0.0.1:8188/prompt", data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

def wait_for_prompt(prompt_id):
    print(f"Waiting for prompt {prompt_id}...")
    while True:
        try:
            req = urllib.request.Request("http://127.0.0.1:8188/history/" + prompt_id)
            with urllib.request.urlopen(req) as resp:
                history = json.loads(resp.read().decode('utf-8'))
                if prompt_id in history:
                    outputs = history[prompt_id].get("outputs", {})
                    if "8" in outputs and "images" in outputs["8"]:
                        return outputs["8"]["images"][0]["filename"]
        except Exception as e:
            print("History query error:", e)
        time.sleep(2)

for filename, prompt_text, caption in tasks:
    print(f"\n==========================================")
    print(f"Generating scene with minimal-line-explainer: {filename}")
    print(f"Prompt: {prompt_text}")
    print(f"==========================================")
    
    tag = filename.replace(".png", "")
    prefix = f"RobotStar_{tag}"
    base_wf["3"]["inputs"]["text"] = prompt_text
    base_wf["8"]["inputs"]["filename_prefix"] = prefix
    base_wf["6"]["inputs"]["seed"] = random.randint(100000, 99999999)
    
    res = queue_prompt(base_wf)
    prompt_id = res["prompt_id"]
    out_filename = wait_for_prompt(prompt_id)
    
    src_path = os.path.join(OUTPUT_DIR, out_filename)
    dst_path = os.path.join(ASSET_DIR, filename)
    print(f"✓ Generated raw image: {src_path}")
    
    gen_img = Image.open(src_path).convert("RGB")
    gen_img = gen_img.resize((860, 860), Image.Resampling.LANCZOS)
    
    master_canvas = Image.new("RGB", (1024, 1536), color=(255, 255, 255))
    master_canvas.paste(gen_img, (82, 580))
    
    draw = ImageDraw.Draw(master_canvas)
    try:
        font = ImageFont.truetype(FONT_PATH, 38)
    except Exception:
        font = ImageFont.load_default()
    draw.text((80, 140), caption, fill=(20, 20, 20), font=font)
    
    master_canvas.save(dst_path)
    print(f"✓ Saved master plate: {dst_path}")

print("\nAll robot-star scenes generated successfully!")
