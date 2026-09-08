# Contributing to Videofy 🎬

Thank you for your interest in improving **Videofy**! Whether you want to add new video presets, contribute 3D LUT profiles, enhance AI auto-framing, or optimize hardware acceleration, this guide will help you get started.

---

## 🏗️ Architecture Overview

```
videofy/
├── render_template.py        # Unified CLI command
├── video_templates/
│   ├── core/                 # Core engine components
│   │   ├── accel.py          # Multi-vendor GPU hardware acceleration (NVENC, QSV, VideoToolbox, VAAPI)
│   │   ├── beat_sync.py      # AI musical downbeat & transient detection
│   │   ├── smart_crop.py     # AI subject & face tracking for 16:9 -> 9:16 reframing
│   │   ├── conformer.py      # Video scaling, aspect cropping & Ken Burns motion
│   │   ├── polaroids.py      # Polaroid snapshot generation with EXIF orientation correction
│   │   ├── grading.py        # 3D LUT resolver and calibrated tone curves
│   │   ├── overlays.py       # Kinetic typography, gold progress bars, glassmorphism cards
│   │   ├── audio.py          # Broadcast EBU R128 loudness mastering & audio bed mixing
│   │   └── qc.py             # Multi-frame visual contact sheet generator
│   └── presets/              # Standard video production presets
│       ├── insta_catchy_reel.py
│       ├── cinematic_landscape.py
│       ├── lifestyle_vlog.py
│       └── fast_cuts_short.py
├── assets/
│   ├── luts/                 # 250+ curated 3D .cube LUT profiles
│   └── ambient_sfx/          # Atmospheric field recordings
└── bg_music/                 # Curated soundtrack library
```

---

## 🧩 Adding a New Preset (3 Simple Steps)

Videofy is designed around an extensible plugin architecture:

1. **Create the preset file**:
   Create a new file in `video_templates/presets/my_new_preset.py` implementing a `render` function:
   ```python
   from ..core.conformer import conform_clip
   from ..core.grading import get_color_filter
   from ..core.overlays import build_timeline_overlays
   from ..core.audio import resolve_audio, build_audio_filter
   from ..core.qc import generate_contact_sheet

   def render(footage_dir, output_file, qc_file=None, title="TITLE", **kwargs):
       # Your custom timeline logic here...
       pass
   ```

2. **Register the preset**:
   Add it to `video_templates/presets/__init__.py`:
   ```python
   from . import my_new_preset

   PRESETS = {
       ...
       "my_new_preset": my_new_preset.render,
   }
   ```

3. **Verify via CLI**:
   Run your preset immediately with:
   ```bash
   python3 render_template.py --preset my_new_preset --footage "path/to/footage"
   ```

---

## 🎨 Contributing 3D LUT Packs

1. Place `.cube` LUT files into a subfolder under `assets/luts/` (e.g. `assets/luts/MyPack/`).
2. Ensure file names are descriptive (e.g. `SunsetWarmth.cube`, `VintageFilm_D65.cube`).
3. The engine will automatically discover and index your LUT via recursive search.

---

## 🧪 Development & Testing

1. **Set up environment**:
   ```bash
   git clone https://github.com/Tamoghna12/videofy.git
   cd videofy
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   pip install flake8 pytest
   ```

2. **Run lint and syntax checks**:
   ```bash
   flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
   ```

3. **Test CLI execution**:
   ```bash
   python3 render_template.py --list-presets
   python3 render_template.py --list-luts
   python3 render_template.py --info
   ```

---

## 📤 Pull Request Checklist

- [ ] Does your code follow existing formatting and docstring styles?
- [ ] Are all new modules imported and exported cleanly in `__init__.py`?
- [ ] Have you tested the preset/tool with both 9:16 and 16:9 footage?
- [ ] Are binary deliverables (`.mp4`), logs, and raw footage excluded from the commit?

Happy building! 🚀
