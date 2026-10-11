# ComfyUI Low-VRAM Story Animation Pipeline

Automated pipeline integrating **ComfyUI** (SD 1.5 + LoRA on low-VRAM GPUs) with **Remotion** via [story-to-handdrawn-video](https://github.com/gnipbao/story-to-handdrawn-video) to turn text stories into silent hand-drawn animated videos.

> **Designed for AI Agents**: This project is optimized for AI coding agents (Claude Code, Gemini/Antigravity, Cursor, Codex). Agents can read [`AGENTS.md`](AGENTS.md) to understand the hardware limits, file layout, and step-by-step pipeline, then run the entire generation flow autonomously from a simple user story prompt.

---

## Prerequisites

1. **System & GPU**:
   - Linux / WSL2
   - NVIDIA GPU (tested on GTX 1650 Ti 4GB VRAM)
   - FFmpeg with `ffprobe`
   - Node.js >= 20, Python >= 3.10
2. **Chinese Fonts** (for text rendering):
   - `NotoSansSC-Regular.otf` installed at `~/.local/share/fonts/`

---

## Setup & Installation

### 1. Python Environment & ComfyUI
```bash
# Clone ComfyUI core
git clone https://github.com/comfyanonymous/ComfyUI.git

# Create and activate Python virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r ComfyUI/requirements.txt
pip install pillow requests
```

### 2. Download Models
Place checkpoints and LoRAs into `ComfyUI/models/`:
- **Base Checkpoint**: `v1-5-pruned-emaonly.safetensors` -> `ComfyUI/models/checkpoints/`
- **LoRAs**:
  - `Hyper-SD15-8steps-CFG-lora.safetensors` -> `ComfyUI/models/loras/`
  - `COOLKIDS_MERGE_V2.5.safetensors` -> `ComfyUI/models/loras/`

### 3. Setup External Video Renderer (`story-to-handdrawn-video`)
```bash
# Clone the renderer repository alongside this project
git clone https://github.com/gnipbao/story-to-handdrawn-video.git
cd story-to-handdrawn-video
npm install
cd ..

# Setup environment variable
cp .env.example .env
source .env
```

---

## Usage Workflow

### 1. Launch ComfyUI (Low-VRAM)
```bash
./venv/bin/python ComfyUI/main.py --listen 127.0.0.1 --port 8188 --lowvram
```

### 2. Run Full Story-to-Video Pipeline
```bash
source .env
source venv/bin/activate

# 1. Plan story beats with a selected style (e.g. sunlit-storybook, colored-pencil-diary)
python3 story-to-handdrawn-video/scripts/run_story_video.py --input story_robot_star.txt --style sunlit-storybook --mode generate

# 2. Generate artwork plates via ComfyUI
python3 run_full_pipeline.py

# 3. Decompose illustration and caption layers
python3 story-to-handdrawn-video/scripts/run_story_video.py --mode import

# 4. Render video (preserves timestamped MP4 in out/)
python3 story-to-handdrawn-video/scripts/run_story_video.py --mode render --out-name robot_star_video
```

---

## Workflows Included
- `workflows/sd15_hypersd_api.json`: 8-step fast generation (CFG 3.5).
- `workflows/sd15_coolkids_api.json`: 20-step storybook art generation.

---

## Acknowledgements & Attribution
- Video animation and rendering engine: [story-to-handdrawn-video](https://github.com/gnipbao/story-to-handdrawn-video) by [@gnipbao](https://github.com/gnipbao) (MIT License).
- Visual generative engine: [ComfyUI](https://github.com/comfyanonymous/ComfyUI) by [@comfyanonymous](https://github.com/comfyanonymous).