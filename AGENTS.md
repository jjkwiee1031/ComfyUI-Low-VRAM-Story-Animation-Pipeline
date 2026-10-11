# ComfyUI Agent Guidelines & Environment Context

## Hardware & Environment Constraints
- **GPU:** NVIDIA GeForce GTX 1650 Ti (4096 MiB VRAM)
- **RAM:** 7.5 GiB (WSL2 Linux 6.18)
- **Rules:**
  - Always launch ComfyUI with `--lowvram` to avoid WSL2 GPADL memory allocation failures (`dxgkio_create_allocation: Ioctl failed: -12`) during KSampler execution.
  - Always prefer low-VRAM configurations (SD 1.5 + Hyper-SD or LCM).
  - Always use `VAEDecodeTiled` instead of standard `VAEDecode` to avoid OOM errors.
  - Large models (>5B parameters) must use GGUF quantization (Q3/Q4) or cloud offloading.

## Environment & Tooling
- **Virtual Environment:** Located at `venv/`.
  - Calling `./venv/bin/comfy` does NOT require `source venv/bin/activate` (shebang is self-contained).
  - Calling raw Python commands or scripts outside comfy-cli requires `source venv/bin/activate`.
- **Environment Variables:**
  - Run `source .env` to export `STORY_VIDEO_PROJECT=/home/jjk-wsl/comfyui/story-to-handdrawn-video`.
- **ComfyUI Launch:**
  ```bash
  ./venv/bin/python ComfyUI/main.py --listen 127.0.0.1 --port 8188 --lowvram
  ```
- **CLI / API Execution:**
  - `comfy run` defaults to a 120s websocket timeout; use `--timeout 300` for standard generation passes.
  - Alternatively, queue directly via HTTP API (`POST /prompt`, poll `GET /history/{prompt_id}`).

## Workflows & LoRA Models
- **Fast SD 1.5 + Hyper-SD (8 steps, CFG 3.5):**
  - Workflow: `workflows/sd15_hypersd_api.json`
  - Model: `ComfyUI/models/checkpoints/v1-5-pruned-emaonly.safetensors`
  - LoRA: `ComfyUI/models/loras/Hyper-SD15-8steps-CFG-lora.safetensors`
  - Run:
    ```bash
    comfy run --workflow workflows/sd15_hypersd_api.json --wait --timeout 300
    ```
- **Storybook Art SD 1.5 + COOLKIDS (20 steps, CFG 7.0, euler_ancestral):**
  - Workflow: `workflows/sd15_coolkids_api.json`
  - Model: `ComfyUI/models/checkpoints/v1-5-pruned-emaonly.safetensors`
  - LoRA: `ComfyUI/models/loras/COOLKIDS_MERGE_V2.5.safetensors`

## Story-to-Handdrawn-Video Pipeline
- **Project Location:** `/home/jjk-wsl/comfyui/story-to-handdrawn-video`
- **Skill Documentation:** `.agents/skills/story-to-handdrawn-video/SKILL.md`
- **Automation Pipeline Script:** `run_full_pipeline.py` (generates scenes, renders text, formats master plates).
- **CJK Fonts:**
  - Font path: `~/.local/share/fonts/NotoSansSC-Regular.otf`.
  - Any script rendering text onto master plates must use this font to prevent tofu boxes `[][][][]`.

### End-to-End Execution Flow (ComfyUI + Story Video):
1. **Plan & Generate Manifest (Choose from 297+ styles):**
   - List available styles:
     ```bash
     source .env
     python3 story-to-handdrawn-video/scripts/run_story_video.py --list-styles
     ```
   - Generate beat sheet & image prompts with selected `--style`:
     ```bash
     python3 story-to-handdrawn-video/scripts/run_story_video.py --input <story.txt> --style <style-name> --mode generate
     ```
     *(Default: `colored-pencil-diary`. Popular alternatives: `sunlit-storybook`, `ink-wash`, `emotional-watercolor-sketch`, `nordic-gouache-storybook`, `minimal-line-explainer`, `kid-crayon`)*.
     Reads story, creates scene beats, and outputs job manifest in `story-to-handdrawn-video/codex-image-jobs.json`.
2. **Generate Scene Master Artwork via ComfyUI:**
   - Execute `python3 run_full_pipeline.py` or post prompts directly to ComfyUI.
   - Master images are saved to `public/assets/generated/codex/<story-dir>/<scene>_master.png` with text rendered using `NotoSansSC-Regular.otf`.
3. **Import & Process Layers:**
   ```bash
   source .env
   python3 story-to-handdrawn-video/scripts/run_story_video.py --mode import
   ```
   Splits caption plate and illustration plate, derives black-and-white ink layer, and updates `storyboard.json`.
4. **Render Video (Preserves previous files without overwriting):**
   - Use `run_story_video.py --mode render` (or pass `--out-name <name>`) which automatically archives and preserves timestamped MP4s in `out/`:
     ```bash
     python3 story-to-handdrawn-video/scripts/run_story_video.py --mode render
     # Or with custom name:
     python3 story-to-handdrawn-video/scripts/run_story_video.py --mode render --out-name story_warm_flat
     ```
   - Preview: `python3 story-to-handdrawn-video/scripts/run_story_video.py --mode preview`
