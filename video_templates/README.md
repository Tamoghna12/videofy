# 🎬 Modular Video Templates Engine

A production-grade, extensible video templating and batch rendering system built on top of FFmpeg, Pillow, and MCP video tools (`kinocut`, `claudeclip`).

---

## 🌟 Overview

The **Video Templates Engine** standardizes the creation of high-impact travel, lifestyle, and social reels across the entire footage library. Instead of writing custom timeline assembly scripts for every location, you can render polished, color-graded, and audio-mastered deliverables from any raw footage directory using a single command.

---

## 🚀 Quick Start (CLI)

```bash
# 1. List available presets
python3 render_template.py --list-presets

# 2. List available 3D LUTs (250+ film & creative LUTs)
python3 render_template.py --list-luts

# 3. List open-source background music tracks & sound effects
python3 render_template.py --list-music
python3 render_template.py --list-sfx

# 4. Render an Instagram Catchy Reel (9:16 Portrait)
python3 render_template.py \
  --preset insta_catchy_reel \
  --footage "raw_footage/Northern Ireland/dunluce_castle" \
  --title "DUNLUCE CASTLE" \
  --subtitle "Medieval Coastal Fortress" \
  --duration 35 \
  --music "solas_jamie_duffy.mp3" \
  --sfx "ocean_waves_crashing.mp3" \
  --lut "CINECOLOR_GOLDEN_HOUR.CUBE" \
  --output "edit/dunluce_castle_reel.mp4" \
  --qc "edit/verify/qc_dunluce.png"

# 4. Render a 16:9 4K/1080p Cinematic Landscape Widescreen
python3 render_template.py \
  --preset cinematic_landscape \
  --footage "raw_footage/Northern Ireland/causeway_coast" \
  --title "GIANT'S CAUSEWAY" \
  --subtitle "Wonders of the Antrim Coast" \
  --lut "Rec709 Kodak 2383 D65.cube" \
  --music "experience_einaudi.mp3" \
  --output "edit/causeway_cinematic.mp4"

# 5. Render a Lifestyle Vlog (Warm Culinary & Calm Reset)
python3 render_template.py \
  --preset lifestyle_vlog \
  --footage "raw_footage/bradford" \
  --title "BRADFORD EVENING" \
  --subtitle "Curry Capital Dining & City Stroll" \
  --grade "culinary_warm" \
  --music "debussy_clair_de_lune.mp3" \
  --output "edit/bradford_lifestyle.mp4"

# 6. Render a Fast Cuts Short (15–18s TikTok / YouTube Shorts)
python3 render_template.py \
  --preset fast_cuts_short \
  --footage "raw_footage/scarboro" \
  --title "SCARBOROUGH QUICK" \
  --subtitle "North Sea Summer" \
  --music "memory_reboot.mp3" \
  --duration 18 \
  --output "edit/scarboro_short.mp4"
```

---

## 📦 Preset Catalog

| Preset | Aspect Ratio | Pacing | Key Features | Default Music |
| :--- | :---: | :---: | :--- | :--- |
| `insta_catchy_reel` | 9:16 (1080x1920) | Dynamic (2.4s photos, 4.5s videos) | Interwoven Polaroid cards, 0.14s white shutter flashes, gold top progress bar, frosted glass cards | `happy_summer.mp3` or `solas_jamie_duffy.mp3` |
| `cinematic_landscape` | 16:9 (1920x1080) | Slow & Majestic (5.5s clips) | 3D print film emulation (Kodak 2383), Ken Burns push-in, subtle bottom title pills, outro card | `experience_einaudi.mp3` |
| `lifestyle_vlog` | 9:16 (1080x1920) | Relaxed & Cozy (4.8s clips) | Calibrated warm culinary curve (`culinary_warm`), muted aesthetic, minimal sans-serif typography | `debussy_clair_de_lune.mp3` |
| `fast_cuts_short` | 9:16 (1080x1920) | Rapid-fire (1.6–2.0s clips) | High energy, fast cuts, punchy intro card, optimized for TikTok & Shorts retention | `memory_reboot.mp3` |

---

## 🛠️ Architecture & Modules

```
video_templates/
├── __init__.py               # Package exports & version
├── mcp_bridge.py             # Bridge to kinocut / claudeclip MCP tools & stream validation
├── render_template.py        # Unified CLI command
├── core/
│   ├── __init__.py           # Core toolchain exports
│   ├── conformer.py          # 9:16 and 16:9 conformer, smart crop, Ken Burns drift
│   ├── polaroids.py          # Polaroid generation with EXIF orientation fix & animated card video
│   ├── grading.py            # Universal 3D LUT resolver + calibrated tone curves
│   ├── overlays.py           # Typography engine, glassmorphism badges, progress bars, outro cards
│   ├── audio.py              # EBU R128 loudness normalization (-16 LUFS) & multi-track ducking
│   └── qc.py                 # Multi-frame visual contact sheet generator
└── presets/
    ├── __init__.py           # Preset registry
    ├── insta_catchy_reel.py  # Instagram catchy reel preset
    ├── cinematic_landscape.py# 16:9 widescreen landscape preset
    ├── lifestyle_vlog.py     # Slow lifestyle vlog preset
    └── fast_cuts_short.py    # Fast cuts TikTok/Shorts preset
```

---

## 🎨 Creative Grading & 3D LUTs

Over 250 industry-standard 3D `.cube` LUTs are indexed under `assets/luts/`:
- **Creative / Travel**: `CINECOLOR_GOLDEN_HOUR.CUBE`, `Summer_Vibes`, `Teal_and_Orange`
- **Film Emulation**: `Rec709 Kodak 2383 D65.cube`, `Fujifilm 3513DI`, `Filmic Resolve`
- **Built-in Calibrated Curves**:
  - `summer_vibrant`: S-curve boost with +14% saturation and lift in shadows.
  - `culinary_warm`: Warm gamma lift and gentle contrast for food/interiors.
  - `clean_landscape`: High clarity, preserved natural blues and greens.
  - `moody_contrast`: Crushed blacks and desaturated highlights for dramatic tones.

---

## 🎧 Audio Engineering & Open-Source Library
 
All presets enforce strict broadcast standards:
- **EBU R128 Loudness**: Normalized to **-16.0 LUFS** (social media target) with a **-1.0 dBFS true peak ceiling**.
- **Multi-Track Mixing**: Background music automatically ducks under ambient field audio / waves / wind.
- **Mastering**: Clean 1.5s audio fade-ins and exponential fade-outs to eliminate clipping.
- **Transparent Audio Suite**: 18 studio-grade SFX (`transitions`, `foley_ui`, `ambience`) and 16 curated BGM tracks cataloged in `assets/audio/manifest.json`.
- **Procedural DSP Synthesis**: 100% public domain CC0 transition whooshes, risers, sub-bass drops, camera shutters, and vinyl crackle generated via `download_audio_library.py`.

---

## 🎙️ AI Cloned Voiceover & Kinetic Highlighted Subtitles

Videofy integrates local, offline zero-shot cloned voiceover synthesis using **Qwen3-TTS 0.6B Base** on NVIDIA GPU:
- **Spaced Contemplative Pacing**: Divides narration into spaced emotional phrases across the timeline (`--voiceover "Phrase 1 | Phrase 2 | Phrase 3"`), delivering an unhurried cadence (`--voiceover-speed 0.92`).
- **Dynamic Multi-Interval Sidechain Ducking**: Background music automatically dips to 20% during each spoken phrase and dynamically swells back to 100% during gaps, allowing emotional soundtrack progressions to breathe.
- **Kinetic Karaoke Subtitle Highlighting**: Uses `faster_whisper` to extract exact word timings and renders real-time highlighted ASS subtitles where the active spoken word glows in radiant gold (`#FFD700`) while surrounding words stay in soft silver.

```bash
python3 render_template.py \
  --preset insta_catchy_reel \
  --footage "raw_footage/york/day1_part1" \
  --title "YORK IN THE RAIN" \
  --subtitle "A Journey Through Time" \
  --voiceover "Two hundred and fifty years... to carve these stones. | Walking the Shambles in the quiet afternoon rain. | Some places don't belong to the past. They're just waiting for you." \
  --voiceover-speed 0.92 \
  --music "solas_jamie_duffy" \
  --sfx "gentle_rain_ambience" \
  --lut "CINECOLOR_GOLDEN_HOUR.CUBE" \
  --beat-sync \
  --output "edit/reels_9x16/york_voiceover_story_reel.mp4"
```

---

## 🧩 Adding a New Preset

Adding a new preset takes 3 simple steps:
1. Create `video_templates/presets/my_new_preset.py` implementing `def render(footage_dir, output_file, ...):`.
2. Import it in `video_templates/presets/__init__.py` and register it in the `PRESETS` dictionary.
3. The preset is instantly available on the CLI via `python3 render_template.py --preset my_new_preset`.
