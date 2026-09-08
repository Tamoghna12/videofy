# 🎬 Videofy

> **Production-Grade Automated Video Editing & Templating Engine**  
> Build viral social reels (9:16) and cinematic widescreen films (16:9) with color grading, kinetic motion graphics, and broadcast audio mastering — all with a single CLI command.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-5.0+-green.svg)](https://ffmpeg.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🌟 Highlights

- ⚡ **1-Click Video Production**: Turn raw footage folders into polished, social-ready reels and widescreen films without manual timeline editing.
- 🎨 **250+ Curated 3D LUTs**: Universal `.cube` grading profiles including legendary Hollywood print stocks (*Kodak 2383, Fujifilm 3513DI*), Golden Hour warmth, Teal & Orange, and camera Log profiles (*Sony S-Log3, DJI D-Log, Panasonic V-Log, ARRI LogC*).
- 📸 **Dynamic Polaroid Motion Graphics**: Generates realistic Polaroid photo cards with auto EXIF orientation correction, dynamic tilt angles, drop shadows, 0.14s white shutter flashes, and ambient blurred background drift.
- 📊 **Kinetic Overlays & Typography**: Smooth animated gold progress bars, glassmorphism title badges, dynamic lower-third location pills, and outro call-to-action cards.
- 🎧 **Broadcast Audio Mastering**: Enforces strict **EBU R128** loudness normalization (**-16 LUFS** for reels, **-14 LUFS** for landscape) with automated background music ducking under ambient field audio.
- 🔍 **Automated Visual QC**: Generates high-resolution multi-frame visual contact sheets for instant visual inspection.

---

## 🚀 Quick Start

### 1. Prerequisites

Ensure **FFmpeg** and **Python 3.9+** are installed:

```bash
# Ubuntu / Debian
sudo apt update && sudo apt install -y ffmpeg fonts-liberation

# macOS
brew install ffmpeg

# Install Python requirements
pip install -r requirements.txt
```

### 2. Inspect Available Presets & 3D LUTs

```bash
# List all 4 built-in video presets
python3 render_template.py --list-presets

# List all 250+ available 3D LUTs
python3 render_template.py --list-luts
```

### 3. 1-Click Rendering Commands

```bash
# Render an Instagram Catchy Reel (9:16 Portrait with Polaroid cards & shutter flashes)
python3 render_template.py \
  --preset insta_catchy_reel \
  --footage "path/to/raw_footage" \
  --title "DUNLUCE CASTLE" \
  --subtitle "Medieval Coastal Fortress" \
  --duration 35 \
  --music "solas_jamie_duffy.mp3" \
  --lut "CINECOLOR_GOLDEN_HOUR.CUBE" \
  --output "edit/dunluce_castle_reel.mp4" \
  --qc "edit/verify/qc_dunluce.png"

# Render a 16:9 Widescreen Film (Kodak 2383 Print Stock & Orchestral Crescendo)
python3 render_template.py \
  --preset cinematic_landscape \
  --footage "path/to/landscape_footage" \
  --title "GIANT’S CAUSEWAY" \
  --subtitle "Wonders of the Antrim Coast" \
  --lut "Rec709 Kodak 2383 D65.cube" \
  --music "experience_einaudi.mp3" \
  --output "edit/causeway_cinematic.mp4"

# Render a Lifestyle Vlog (Warm culinary tone curve & chill acoustic reset)
python3 render_template.py \
  --preset lifestyle_vlog \
  --footage "path/to/vlog_footage" \
  --title "BRADFORD EVENING" \
  --subtitle "Curry Capital Dining & City Stroll" \
  --grade "culinary_warm" \
  --music "debussy_clair_de_lune.mp3" \
  --output "edit/bradford_lifestyle.mp4"

# Render a Fast Cuts Short (15–20s rapid-fire TikTok / Shorts micro-reel)
python3 render_template.py \
  --preset fast_cuts_short \
  --footage "path/to/footage" \
  --title "YORK QUICK" \
  --subtitle "15 Seconds of Heritage" \
  --music "memory_reboot.mp3" \
  --duration 18 \
  --output "edit/york_short.mp4"
```

---

## 📦 Preset Catalog

| Preset | Aspect Ratio | Target Duration | Visual Design & Motion Graphics | Sound & Grading |
| :--- | :---: | :---: | :--- | :--- |
| **`insta_catchy_reel`** | 9:16 (1080&times;1920) | 25–45s | Interwoven Polaroid photo cards, EXIF auto-rotation, 0.14s white shutter flashes, animated gold progress bar, frosted glass cards | Upbeat music (`solas` / `summer_pop`), ambient waves ducking, EBU R128 (-16 LUFS) |
| **`cinematic_landscape`** | 16:9 (1920&times;1080) | 45–90s | Widescreen landscape, slow Ken Burns push-in, subtle bottom title pills, outro CTA card | Print film emulation (Kodak 2383 D65), orchestral crescendo (`experience_einaudi`) |
| **`lifestyle_vlog`** | 9:16 (1080&times;1920) | 30–60s | Warm culinary curve, relaxed pacing, minimal typography, travel journal aesthetics | Chill piano / lo-fi (`debussy_clair_de_lune`), gentle wind |
| **`fast_cuts_short`** | 9:16 (1080&times;1920) | 15–20s | Rapid-fire cuts (1.6–2.0s), punchy typography, high retention hook | Synthwave / beat drops (`memory_reboot`) |

---

## 🏗️ Architecture & Modules

```
videofy/
├── render_template.py        # Unified CLI command runner
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
├── video_templates/          # Core templating engine package
│   ├── __init__.py           # Package exports & version
│   ├── mcp_bridge.py         # MCP tool connectors (kinocut/claudeclip) & stream validation
│   ├── core/
│   │   ├── conformer.py      # Video conforming, aspect-ratio smart crop & Ken Burns drift
│   │   ├── polaroids.py      # Polaroid generation with EXIF transpose & motion cards
│   │   ├── grading.py        # Universal 3D LUT resolver + calibrated tone curves
│   │   ├── overlays.py       # Kinetic typography, progress bars, lower-thirds & outro CTAs
│   │   ├── audio.py          # EBU R128 mastering (-16 LUFS) & multi-track ducking
│   │   └── qc.py             # Multi-frame visual contact sheet generator
│   └── presets/
│       ├── insta_catchy_reel.py   # 9:16 Catchy Instagram reel preset
│       ├── cinematic_landscape.py # 16:9 Cinematic widescreen preset
│       ├── lifestyle_vlog.py      # 9:16 Cozy lifestyle vlog preset
│       └── fast_cuts_short.py     # 9:16 Fast cuts TikTok/Shorts preset
├── assets/
│   ├── luts/                 # 250+ curated 3D .cube LUT profiles
│   └── ambient_sfx/          # Cathedral bells, ocean waves, train rolling, gentle rain
├── bg_music/                 # Curated soundtrack library (classical, lofi, upbeat)
└── create_york_detailed_reels.py  # Production scripts for regional travel series
```

---

## 🎨 Creative Grading & 3D LUTs

Over 250 industry-standard 3D `.cube` LUTs are organized under `assets/luts/`:
- **Film Emulation**: `Rec709 Kodak 2383 D65.cube`, `Fujifilm 3513DI`, `Filmic Resolve`
- **Creative Travel**: `CINECOLOR_GOLDEN_HOUR.CUBE`, `Summer_Vibes`, `Teal_and_Orange`
- **Calibrated Built-In Curves**:
  - `summer_vibrant`: S-curve boost with +14% saturation and lifted midtones.
  - `culinary_warm`: Warm gamma lift and gentle contrast for food & interiors.
  - `clean_landscape`: High clarity, preserved natural blues and greens.
  - `moody_contrast`: Crushed blacks and desaturated highlights for dramatic tones.

---

## 🧩 Adding a Custom Preset

Adding a new preset takes 3 simple steps:
1. Create `video_templates/presets/my_custom_preset.py` implementing `def render(footage_dir, output_file, ...):`.
2. Register it in `video_templates/presets/__init__.py`.
3. The preset becomes immediately executable via `python3 render_template.py --preset my_custom_preset`.

---

## 📜 License

MIT License. See [LICENSE](LICENSE) for details.
