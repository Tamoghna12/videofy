# Videofy Project Guidelines & Architecture Reference

## Workspace Structure
- **Production Hierarchy**: `01_raw_footage/`, `02_assets/`, `03_engine/`, `04_deliverables/` (mirrored to `raw_footage/`, `assets/`, `video_templates/`, `edit/`).
- **Declarative Recipes**: Always define video projects as YAML files under `projects/`. Never add redundant runner scripts to the workspace root.
- **Unified Runner**: Use `python3 render_template.py -c projects/<recipe>.yaml` (with `--validate` for dry-run).

## Hardware & Portability
- **Hardware Acceleration**: Auto-detects Intel Arc (`xpu`/`h264_qsv`), NVIDIA (`cuda`/`h264_nvenc`), Apple Silicon (`h264_videotoolbox`), or CPU (`libx264`).
- **Voiceover Engine**: Connects dynamically to Qwen-TTS with cloned voice profile `assets/audio/voice/tee_voice_16k.wav`. Supports frame-accurate shot-locked narration, automated ducking (-15dB), and kinetic ASS typography.
- **Color Grading**: 250+ LUTs in `assets/luts/` + Kodak 2383 film emulation and D-Log M color conformers.

## Deliverables & QC
- Render outputs to `edit/reels_9x16/` (9:16) or `edit/cinematic_16x9/` (16:9).
- Generate and inspect visual QC contact sheets in `edit/verify/qc_sheet_*.png`.
- Ensure photos in Polaroid cards are authentic and labeled accurately.
