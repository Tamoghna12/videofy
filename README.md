# 🎬 Videofy

> **Production-Grade Automated Video Editing & Templating Engine**  
> Build viral social reels (9:16) and cinematic widescreen films (16:9) with AI beat-sync, dynamic smart-cropping, 3D LUT color grading, kinetic motion graphics, and multi-vendor GPU acceleration.

[![CI Pipeline](https://github.com/Tamoghna12/videofy/actions/workflows/ci.yml/badge.svg)](https://github.com/Tamoghna12/videofy/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-5.0+-green.svg)](https://ffmpeg.org/)
[![Hardware Acceleration](https://img.shields.io/badge/GPU-NVENC%20%7C%20Intel%20QSV%20%7C%20Apple%20VT-orange.svg)](#-multi-vendor-gpu-hardware-acceleration)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📸 Visual Showcase

| 9:16 Instagram Catchy Reel | 9:16 York Heritage Travel Reel |
| :---: | :---: |
| ![Dunluce Castle Reel Preview](docs/images/qc_sheet_dunluce_template.png) | ![York Day 1 Reel Preview](docs/images/qc_sheet_york_day1_part1.png) |

---

## 🌟 Highlights

- ⚡ **1-Click Video Production**: Turn raw footage folders into polished, social-ready reels and widescreen films without manual timeline editing.
- 🚀 **Multi-Vendor GPU Acceleration**: Native hardware encoding for **NVIDIA NVENC** (`h264_nvenc`), **Intel Arc & Core Ultra Quick Sync** (`h264_qsv` / `h264_vaapi`), and **Apple Silicon** (`h264_videotoolbox`) with automatic CPU fallback.
- 🎵 **AI Beat-Drop Synchronization**: Analyzes audio transients and rhythm downbeats to snap video cuts, photo card reveals, and shutter flashes directly to musical beat drops.
- 🎯 **AI Smart Cropping & Auto-Framing**: Detects faces and visual saliency via OpenCV to dynamically pan the 9:16 crop window across 16:9 footage, ensuring subjects are always centered.
- 🎨 **250+ Curated 3D LUTs**: Universal `.cube` grading profiles including legendary Hollywood print stocks (*Kodak 2383, Fujifilm 3513DI*), Golden Hour warmth, Teal & Orange, and camera Log profiles (*Sony S-Log3, DJI D-Log, Panasonic V-Log, ARRI LogC*).
- 📸 **Dynamic Polaroid Motion Graphics**: Generates realistic Polaroid photo cards with auto EXIF orientation correction, dynamic tilt angles, drop shadows, 0.14s white shutter flashes, and ambient blurred background drift.
- 📊 **Kinetic Overlays & Typography**: Smooth animated gold progress bars, glassmorphism title badges, dynamic lower-third location pills, and outro call-to-action cards.
- 🎧 **Broadcast Audio Mastering**: Enforces strict **EBU R128** loudness normalization (**-16 LUFS** for reels, **-14 LUFS** for landscape) with automated background music ducking under ambient field audio.
- 🎙️ **AI Zero-Shot Cloned Voiceover**: Generates personal narrative storytelling on local GPU via Qwen3-TTS using your voice sample, with automated broadcast-grade sidechain music ducking (-15dB).
- 🔍 **Automated Visual QC**: Generates high-resolution multi-frame visual contact sheets for instant visual inspection.

---

## 🚀 Quick Start & Multi-Device Setup

Clone the repository to any machine (Linux, macOS, Windows with WSL2):

```bash
git clone https://github.com/Tamoghna12/videofy.git
cd videofy
```

### 1. Prerequisites

Ensure **FFmpeg** and **Python 3.9+** are installed:

```bash
# Ubuntu / Debian
sudo apt update && sudo apt install -y ffmpeg fonts-liberation

# macOS
brew install ffmpeg

# Install Core Python Dependencies
pip install -r requirements.txt
```

### 2. (Optional) Intel Arc GPU Acceleration (XPU)

If running on an **Intel Arc GPU** (e.g. Arc A770, A750, A380, B580, or Intel Core Ultra Arc integrated graphics):

```bash
# Install Intel Level-Zero compute runtime
sudo apt install -y intel-opencl-icd intel-level-zero-gpu

# Install PyTorch with native Intel XPU support
pip install torch torchvision --index-url https://download.pytorch.org/whl/xpu
```

### 3. Check System Hardware Acceleration

Check your active GPU encoder, hardware acceleration, and voiceover engine:

```bash
python3 render_template.py --info
```

Example output:
```text
⚡ System & Hardware Acceleration Status:
======================================================================
  Active Encoder     : h264_nvenc (NVENC)
  Available Encoders :
    • h264_nvenc (NVIDIA)                 : ✅ YES
    • h264_qsv (Intel Arc / QuickSync)    : ❌ NO
    • h264_videotoolbox (Apple Silicon)   : ❌ NO
    • h264_vaapi (Linux VAAPI)            : ❌ NO
    • libx264 (Universal CPU)             : ✅ YES
======================================================================
```

### 4. Inspect Available Presets & 3D LUTs

```bash
# List all built-in video presets
python3 render_template.py --list-presets

# List all 250+ available 3D LUTs
python3 render_template.py --list-luts

# List categorized open-source background music tracks
python3 render_template.py --list-music

# List studio-grade sound effects (transitions, foley, ambience)
python3 render_template.py --list-sfx

# Automatically download and synthesize the complete audio library (100% offline & CC0/Open Source)
python3 render_template.py --download-audio
```

### 5. Declarative Project Recipes (Recommended for 100% Reproducibility)

Instead of passing dozens of CLI flags or writing ad-hoc Python scripts, define your videos as declarative **YAML recipes** in the `projects/` directory:

```bash
# Validate project configuration, shot timing, and media paths without rendering
python3 render_template.py --project projects/loughborough_campus_journey.yaml --validate

# Render the complete film with GPU acceleration, letterbox frames, and voiceover
python3 render_template.py --project projects/loughborough_campus_journey.yaml

# Batch render multiple projects simultaneously
python3 render_template.py --project projects/bradford_*.yaml
```

#### Example Project Recipe (`projects/loughborough_campus_journey.yaml`):
```yaml
name: "Loughborough University Campus Journey"
preset: "cinematic_landscape"
title: "LOUGHBOROUGH UNIVERSITY"
subtitle: "LEICESTERSHIRE • CAMPUS WALK"
outro_title: "LOUGHBOROUGH UNIVERSITY"
outro_subtitle: "Where Passion Shapes the Future 📍"
handle: "@tamoghna.travels"

footage_dir: "01_raw_footage/lboro_university"
output_file: "edit/cinematic_16x9/lboro_university_campus_journey.mp4"
qc_file: "edit/verify/qc_sheet_lboro_journey.png"

grade: "odyssey"     # 2001: A Space Odyssey 70mm balanced filmic look
music: "beethoven_symphony_no6_pastoral.mp3"
sfx: "forest_birds_wind.mp3"
black_bars: true

voiceover:
  speed: 0.91
  text: >-
    There is a quiet clarity in the morning air when you start walking towards campus... |
    Passing down Epinal Way, you are greeted by Loughborough University...

shots:
  - file: "DJI_20251027141310_0022_D.MP4"
    start: 0.5
    end: 6.0
    caption: "MORNING COMMUTE // LEICESTERSHIRE APPROACH"
  - file: "DJI_20251027142035_0025_D.MP4"
    start: 0.5
    end: 9.5
    caption: "LOUGHBOROUGH UNIVERSITY // MAIN GATEWAY"
```

---

### 6. Ad-hoc CLI Flag Rendering Commands

```bash
# Render an Instagram Catchy Reel with AI Beat-Sync & GPU Acceleration
python3 render_template.py \
  --preset insta_catchy_reel \
  --footage "path/to/raw_footage" \
  --title "DUNLUCE CASTLE" \
  --subtitle "Medieval Coastal Fortress" \
  --duration 35 \
  --music "happy_summer.mp3" \
  --lut "CINECOLOR_GOLDEN_HOUR.CUBE" \
  --accel auto \
  --beat-sync \
  --smart-crop \
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

# Render a Storytelling Reel with AI Cloned Voiceover & Music Ducking
python3 render_template.py \
  --preset insta_catchy_reel \
  --footage "raw_footage/york/day1_part1" \
  --title "YORK IN THE RAIN" \
  --subtitle "A Journey Through Time" \
  --voiceover "They spent two hundred and fifty years building York Minster. Standing under these stones in the afternoon rain, watching the cobblestones glisten, you realize some places don't belong to the past. They're just waiting for you to slow down." \
  --music "solas_jamie_duffy" \
  --sfx "gentle_rain_ambience" \
  --lut "CINECOLOR_GOLDEN_HOUR.CUBE" \
  --accel auto \
  --beat-sync \
  --output "edit/reels_9x16/york_voiceover_story_reel.mp4" \
  --qc "edit/verify/qc_york_voiceover.png"

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

## ⚡ Multi-Vendor GPU Hardware Acceleration

Videofy automatically detects your system's hardware configuration and routes encoding to the optimal hardware encoder:

| GPU / Platform | Encoder | CLI Flag | Benefits |
| :--- | :--- | :--- | :--- |
| **NVIDIA GeForce / RTX** | `h264_nvenc` | `--accel nvenc` | 5&times;–10&times; faster encoding, low CPU overhead |
| **Intel Arc / Core Ultra** | `h264_qsv` / `h264_vaapi` | `--accel qsv` or `--accel vaapi` | Dedicated Quick Sync hardware, extreme 1080p/4K throughput |
| **Apple Silicon (M1–M4)** | `h264_videotoolbox` | `--accel videotoolbox` | Native Apple Media Engine hardware encoding |
| **AMD Radeon** | `h264_vaapi` | `--accel vaapi` | Linux kernel VAAPI hardware encoding |
| **Universal Fallback** | `libx264` | `--accel cpu` | Runs anywhere with standard CPU threads |

*By default, `--accel auto` selects the fastest available hardware encoder automatically.*

---

## 🎵 AI Beat-Drop Synchronization

Using audio transient analysis and spectral flux onset detection, the `--beat-sync` flag aligns your timeline with the music:
- Computes rhythmic BPM and energy transients.
- Nudges clip cut points and photo card inserts so transitions snap directly to the downbeats.
- Synchronizes the 0.14s white camera shutter flash with snare and kick transients.

---

## 🎯 AI Smart Cropping & Subject Auto-Framing

When converting 16:9 landscape video into 9:16 vertical reels, static center cropping often cuts off subjects on the edges. The `--smart-crop` engine:
- Scans video frames for faces and visual saliency via OpenCV.
- Dynamically centers the crop window around the active focal point.
- Applies a temporal smoothing filter so camera movement feels like an intentional, smooth cinematic pan.

---

## 📦 Preset Catalog

| Preset | Aspect Ratio | Target Duration | Visual Design & Motion Graphics | Sound & Grading |
| :--- | :---: | :---: | :--- | :--- |
| **`insta_catchy_reel`** | 9:16 (1080&times;1920) | 25–45s | Interwoven Polaroid photo cards, EXIF auto-rotation, 0.14s white shutter flashes, animated gold progress bar, frosted glass cards | Upbeat music (`solas` / `summer_pop`), ambient waves ducking, EBU R128 (-16 LUFS) |
| **`cinematic_landscape`** | 16:9 (1920&times;1080) | 45–90s | Widescreen landscape, slow Ken Burns push-in, subtle bottom title pills, outro CTA card | Print film emulation (Kodak 2383 D65), orchestral crescendo (`experience_einaudi`) |
| **`lifestyle_vlog`** | 9:16 (1080&times;1920) | 30–60s | Warm culinary curve, relaxed pacing, minimal typography, travel journal aesthetics | Chill piano / lo-fi (`debussy_clair_de_lune`), gentle wind |
| **`fast_cuts_short`** | 9:16 (1080&times;1920) | 15–20s | Rapid-fire cuts (1.6–2.0s), punchy typography, high retention hook | Synthwave / beat drops (`memory_reboot`) |

---

## 🎧 Open-Source Audio & Sound Effects Library (CapCut-Alternative)

Videofy includes a **100% open-source, fully transparent, royalty-free audio suite** with automated procedural DSP sound generation. Unlike proprietary editing apps (e.g. CapCut, Premiere) with opaque licensing terms, every audio asset in Videofy is clearly documented, attribution-ready, and safe for commercial monetization.

### 1. Studio-Grade Procedural SFX (100% Public Domain CC0)
Synthesized mathematically via pure DSP (`numpy`, `scipy.signal`) to studio-grade **320kbps MP3** at **-12 LUFS** impact normalization:
- **Transitions**:
  - `whoosh_fast`: Snappy 0.55s dynamic transition whoosh with exponential pitch dive.
  - `whoosh_cinematic_deep`: Heavy 1.3s atmospheric trailer sub-whoosh.
  - `whip_pan_swish`: Ultra-fast 0.35s high-velocity camera swish.
  - `sub_bass_drop_boom`: 40Hz sub-bass impact drop with resonant decay.
  - `cinematic_riser_tension`: 3.5s exponential frequency sweep and trailer buildup.
  - `digital_glitch_stutter`: Modern sci-fi digital glitch with rhythmic stutter.
- **Foley & Interface**:
  - `camera_shutter_snap`: Mechanical DSLR dual-curtain click & release.
  - `camera_shutter_burst`: 0.85s rapid-fire continuous motor-drive burst.
  - `vintage_vinyl_crackle`: Warm 15s analog vinyl surface noise and dust crackle loop.
  - `pop_bubble_ui`: Clean minimal acoustic UI bubble pop.
  - `minimal_bell_chime`: Elegant harmonic brass bell chime (E6/B6).
  - `paper_slide_flip`: Textured Polaroid paper slide and card rustle.
  - `cozy_campfire_crackle`: 25s crackling wood hearth and amber flame ambience.

### 2. Environmental Ambience Beds
Broadcast-mastered field audio beds with multi-track auto-ducking (-20 LUFS):
- `ocean_waves_crashing`: Atlantic coastal breaking surf.
- `gentle_rain_ambience`: Calming rain on stone pavement.
- `church_bells_cathedral`: Historic Gothic cathedral bells.
- `train_rolling_ambience`: Vintage railway track rolling and rhythmic click-clack.
- `forest_birds_wind`: Woodland breeze with gentle procedural bird chirps.

### 3. Categorized Soundtrack Catalog
Sorted by mood and tempo with BPM metadata:
- **Travel & Upbeat**: `happy_summer` (118 BPM), `summer_pop_upbeat` (124 BPM)
- **Cinematic & Epic**: `experience_einaudi` (92 BPM), `solas_jamie_duffy` (112 BPM), `interstellar_cornfield_chase` (100 BPM), `can_you_hear_the_music` (132 BPM)
- **Electronic & Synth**: `future_bass_summer` (128 BPM), `memory_reboot` (130 BPM)
- **Classical Heritage (Musopen CC0)**: `debussy_clair_de_lune`, `debussy_arabesque_no1`, `debussy_reverie`, `beethoven_pathetique_adagio`, `beethoven_moonlight_sonata`, `satie_gymnopedie_no1`, `vivaldi_winter_largo`, `bach_cello_suite_no1_prelude`

### 4. Machine & Human-Readable Transparency
- **Manifest**: [assets/audio/manifest.json](assets/audio/manifest.json) — structured metadata with IDs, categories, duration, BPM, licenses, and sources.
- **Licensing Documentation**: [assets/audio/AUDIO_LICENSES.md](assets/audio/AUDIO_LICENSES.md) — full legal attribution declarations and usage guidelines.
- **1-Click Automation**: Run `python3 download_audio_library.py` to regenerate or verify the complete library offline.

---

## 🏗️ Step-by-Step Architecture & Production Hierarchy

Videofy organizes the video editing lifecycle into an intuitive 4-step production hierarchy:

```
videofy/
│
├── projects/                                # [DECLARATIVE RECIPES (100% REPRODUCIBLE)]
│   ├── loughborough_campus_journey.yaml     # 99.5s 16:9 film, 14 shots, Odyssey 70mm, Beethoven Pastoral
│   ├── bradford_reel1_the_journey.yaml      # Yorkshire train commute & Victorian arches
│   ├── bradford_reel2_solo_dining.yaml      # Window views, slow dining & evening reset
│   ├── bradford_reel3_city_hall_twilight.yaml # City Hall & 220-ft clock tower at dusk
│   ├── castlerock_causeway_coast.yaml       # Wild Antrim coast & sand dunes
│   └── dunluce_castle.yaml                  # 1500 cliffside fortress ruins
│
├── 01_raw_footage/ -> raw_footage/          # [STEP 1: INGESTION]
│   ├── bradford/                            # 4K Yorkshire city footage
│   ├── Northern Ireland/                    # Causeway Coast, Dunluce Castle, Castlerock
│   ├── scarboro/                            # Scarborough South Bay
│   ├── whitby/                              # Whitby Abbey & Coastal Harbor
│   ├── york/                                # Day 1 Parts 1 & 2
│   └── incoming_archive/                    # Raw incoming camera clips (2026*.mp4)
│
├── 02_assets/ -> assets/                    # [STEP 2: CREATIVE ASSETS]
│   ├── audio/                               # Open-Source Audio Suite
│   │   ├── voice/                           # Bundled reference voice audio (tee_voice_16k.wav)
│   │   ├── manifest.json                    # Machine-readable metadata, BPM & licenses
│   │   ├── AUDIO_LICENSES.md                # Full legal attribution guide
│   │   ├── sfx/                             # 18 Studio-grade SFX (transitions, foley_ui, ambience)
│   │   └── bg_music/                        # 16 Curated tracks (travel, epic, synth, classic)
│   ├── luts/                                # 250+ Curated 3D .cube LUT profiles
│   └── photos/                              # Photography assets (Whitby, York, Scarboro)
│
├── 03_engine/ -> video_templates/           # [STEP 3: PRODUCTION ENGINE]
│   ├── render_template.py                   # Unified CLI runner (-c/--project, --validate, etc.)
│   ├── download_audio_library.py            # Automated procedural audio & SFX synthesizer
│   ├── video_templates/                     # Core templating package
│   │   ├── core/                            # Qwen-TTS (XPU/CUDA), AI beat-sync, smart crop, conformer, audio
│   │   └── presets/                         # insta_catchy_reel, cinematic_landscape, lifestyle_vlog
│   └── requirements.txt                     # Dependencies (Pillow, numpy, scipy, librosa, opencv, PyYAML, faster-whisper)
│
├── 04_deliverables/ -> edit/                # [STEP 4: FINISHED DELIVERABLES & QC]
│   ├── reels_9x16/                          # Rendered vertical portrait reels (1080x1920)
│   ├── cinematic_16x9/                      # Rendered widescreen films (1920x1080)
│   └── verify/                              # Multi-frame visual QC contact sheets
│
└── _dump/                                   # [QUARANTINE ARCHIVE - Local Only]
    ├── legacy_scripts/                      # Deprecated prototype scripts (auto_cut, insta_reel, etc.)
    ├── temp_render_slices/                  # Temporary intermediate slices & concat lists
    ├── legacy_cards/                        # Previous test polaroid cards
    └── legacy_project_files/                # Old project metadata, edl.json & transcripts
```

---

## 🎨 Creative Grading & 3D LUTs

Over 250 industry-standard 3D `.cube` LUTs are organized under `assets/luts/`:
- **Film Emulation**: `Rec709 Kodak 2383 D65.cube`, `Fujifilm 3513DI`, `Filmic Resolve`
- **Creative Travel**: `CINECOLOR_GOLDEN_HOUR.CUBE`, `Summer_Vibes`, `Teal_and_Orange`
- **Calibrated Built-In Curves**:
  - `odyssey`: Balanced 70mm *2001: A Space Odyssey* aesthetic (Eastman 5254 look: unclipped highlight rolloff, clean neutral midtones, subtle shadow cooling, and contrast-adaptive sharpening).
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

See [CONTRIBUTING.md](CONTRIBUTING.md) for full developer documentation.

---

## 📜 License

MIT License. See [LICENSE](LICENSE) for details.
