# Videofy: Project Context & Agent Memory Guidelines

This document provides persistent context and guidelines for Antigravity/Gemini agents working on the **Videofy** video production and templating repository across different machines.

---

## 1. Project Architecture & 4-Step Production Hierarchy

Videofy uses an intuitive 4-step hierarchy with symlinks:
```
videofy/
├── projects/                                # [DECLARATIVE RECIPES (100% REPRODUCIBLE)]
│   ├── yorkshire_catchy_insta_reel.yaml     # 9:16 Insta reel, Polaroid cards (The Shambles, Whitby Abbey, Scarborough Bay)
│   ├── bradford_architectural_story.yaml    # 16:9 Architectural story with frame-accurate shot-locked voiceover
│   ├── bradford_architectural_cinematic.yaml # 16:9 Pure cinematic widescreen film (Kodak 2383)
│   ├── kolkata_to_loughborough_journey.yaml # 3-part travel odyssey
│   ├── loughborough_campus_journey.yaml     # 99.5s campus film, Odyssey 70mm, Beethoven Pastoral
│   ├── castlerock_causeway_coast.yaml       # Wild Antrim coast & sand dunes
│   └── dunluce_castle.yaml                  # 1500 cliffside fortress ruins
│
├── 01_raw_footage/ -> raw_footage/          # [STEP 1: INGESTION]
│   ├── bradford/                            # 4K Yorkshire city & Victorian architecture footage
│   ├── Northern Ireland/                    # Causeway Coast, Dunluce Castle, Castlerock
│   ├── scarboro/                            # Scarborough South Bay
│   ├── whitby/                              # Whitby Abbey & Coastal Harbour
│   ├── york/                                # Day 1 Parts 1 & 2
│   └── incoming_archive/                    # Raw incoming camera clips
│
├── 02_assets/ -> assets/                    # [STEP 2: CREATIVE ASSETS]
│   ├── audio/                               # Open-Source Audio Suite
│   │   ├── voice/                           # Bundled reference voice audio (tee_voice_16k.wav)
│   │   ├── manifest.json                    # Machine-readable audio metadata & licenses
│   │   ├── AUDIO_LICENSES.md                # Legal attribution guide
│   │   ├── sfx/                             # Studio-grade SFX (waves, train ambience, whooshes)
│   │   └── bg_music/                        # Curated music (Solas, Einaudi, travel, epic)
│   ├── luts/                                # 250+ Curated 3D .cube LUT profiles
│   └── photos/                              # Photography assets:
│       ├── york_shambles.jpg                # Authentic medieval timber-framed cobblestone alley
│       ├── whitby_abbey.jpg                 # Unobstructed 13th-century Gothic cliff ruins
│       └── scarborough_bay.jpg              # Crescent bay and ocean cliffs
│
├── 03_engine/ -> video_templates/           # [STEP 3: PRODUCTION ENGINE]
│   ├── render_template.py                   # Unified CLI runner (-c/--project, --validate)
│   ├── download_audio_library.py            # Audio library downloader / synthesizer
│   └── video_templates/                     # Core templating package
│       ├── core/                            # Conformer, grading, audio, overlays, polaroids, voiceover, beat-sync
│       └── presets/                         # insta_catchy_reel, cinematic_landscape, lifestyle_vlog, fast_cuts_short
│
└── 04_deliverables/ -> edit/                # [STEP 4: RENDERED DELIVERABLES & QC]
    ├── reels_9x16/                          # 9:16 Portrait reels
    ├── cinematic_16x9/                      # 16:9 Widescreen films
    └── verify/                              # Frame-accurate visual QC contact sheets (*.png)
```

---

## 2. Multi-Device & Cross-Platform Execution

When cloning on a new device (Linux laptop, Intel Arc desktop, RTX workstation, or CPU-only server):
1. **Dependencies**:
   ```bash
   pip install -r requirements.txt
   sudo apt-get install -y ffmpeg fonts-liberation
   ```
2. **Audio Verification**:
   If assets are missing:
   ```bash
   python3 download_audio_library.py
   ```
3. **Hardware Acceleration Auto-Detection**:
   - Intel Arc GPU: `ipex` / `torch.device('xpu')` + `h264_qsv`
   - NVIDIA GPU: CUDA + `h264_nvenc`
   - Apple Silicon: `h264_videotoolbox`
   - Universal Fallback: CPU `libx264` + PyTorch CPU
4. **Rendering via Declarative YAML**:
   ```bash
   # Validate without rendering
   python3 render_template.py -c projects/yorkshire_catchy_insta_reel.yaml --validate

   # Execute render
   python3 render_template.py -c projects/yorkshire_catchy_insta_reel.yaml
   ```

---

## 3. Core Engine Guidelines & Conventions

1. **Declarative Recipes Over Ad-Hoc Scripts**:
   - Always define or update recipes in `projects/*.yaml` instead of writing throwaway root scripts.
   - Presets support both automated discovery and curated shot sequences (`shots:` list).
2. **Polaroid Photo Cards**:
   - In `insta_catchy_reel`, photo cards support `title`, `subtitle`, `angle`, `duration`.
   - Ensure photo framing centers on the landmark. Verified photos reside in `assets/photos/`.
3. **Voiceover & Subtitles**:
   - `video_templates/core/voiceover.py` supports zero-shot voice cloning with local Qwen-TTS.
   - Generates spaced story voiceover + kinetic word-highlighted ASS subtitles.
   - Automatically ducks background music by -15dB during narration intervals.
4. **Visual QC Contact Sheets**:
   - Every render should generate a visual QC contact sheet in `edit/verify/qc_sheet_*.png`.
   - Always verify the contact sheet with `view_file` to inspect color grading, framing, text positioning, and letterboxing.
5. **Git & Deliverable Hygiene**:
   - Keep deliverables in `edit/reels_9x16/` and `edit/cinematic_16x9/` with backward-compatible symlinks in `edit/`.
   - Always commit new recipes, core engine enhancements, and verified assets to git and keep `origin/main` in sync.
