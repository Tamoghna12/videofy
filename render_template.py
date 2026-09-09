#!/usr/bin/env python3
"""
render_template.py - Unified Command-Line Interface for Video Template Production.

Enables 1-click batch rendering of high-impact videos (Insta Reels, Cinematic Widescreen,
Lifestyle Vlogs, Fast TikTok Shorts) with multi-vendor GPU acceleration, AI beat-sync,
and AI subject auto-framing.
"""

import argparse
import sys
import json
import yaml
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Add workspace root to sys.path
WORKSPACE_ROOT = Path(__file__).resolve().parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from video_templates.presets import PRESETS
from video_templates.core.accel import get_hardware_info


PRESET_DESCRIPTIONS = {
    "insta_catchy_reel": "9:16 Portrait Reel - Live video + Polaroid photo snaps with shutter flashes, gold progress bar, dynamic lower-thirds, upbeat music, and optional AI beat-sync.",
    "cinematic_landscape": "16:9 Widescreen - Film-look color grading (Kodak 2383), cinematic title cards, gentle Ken Burns push-in, and orchestral soundtrack.",
    "lifestyle_vlog": "9:16 Portrait - Warm culinary tone curve, relaxed pacing, subtle captions, and chill lo-fi/piano vibes.",
    "fast_cuts_short": "9:16 Portrait - 15-20s rapid-fire TikTok/Shorts micro-reel, beat drops, fast cuts, and punchy typography.",
}


def print_presets():
    print("\n🎬 Available Video Templates Presets:")
    print("=" * 70)
    for name, desc in PRESET_DESCRIPTIONS.items():
        print(f"  • {name:<22} : {desc}")
    print("=" * 70 + "\n")


def print_luts():
    lut_dir = WORKSPACE_ROOT / "assets" / "luts"
    if not lut_dir.exists():
        print("No assets/luts directory found.")
        return
    luts = sorted(list(lut_dir.rglob("*.cube")) + list(lut_dir.rglob("*.CUBE")))
    print(f"\n🎨 Available 3D LUTs ({len(luts)} found):")
    print("=" * 70)
    for i, lut in enumerate(luts[:30]):
        print(f"  [{i+1:02d}] {lut.name}")
    if len(luts) > 30:
        print(f"  ... and {len(luts) - 30} more in {lut_dir}")
    print("=" * 70 + "\n")


def print_system_info():
    info = get_hardware_info()
    print("\n⚡ System & Hardware Acceleration Status:")
    print("=" * 70)
    print(f"  Active Encoder     : {info['active_encoder']} ({info['acceleration_type'].upper()})")
    print("  Available Encoders :")
    for enc, avail in info['available_encoders'].items():
        status = "✅ YES" if avail else "❌ NO"
        print(f"    • {enc:<35} : {status}")
    print("=" * 70 + "\n")


def print_music(category=None):
    from video_templates.core.audio import list_audio_items
    items = list_audio_items(kind="music", category=category)
    cat_str = f" [Category: {category}]" if category else ""
    print(f"\n🎵 Videofy Open-Source Music Catalog{cat_str} ({len(items)} tracks):")
    print("=" * 90)
    print(f"  {'ID / Track Name':<28} | {'Category':<18} | {'BPM':<5} | {'License':<15} | {'Mood / Description'}")
    print("-" * 90)
    for item in items:
        bpm = str(item.get("bpm", "--"))
        print(f"  {item['id']:<28} | {item.get('category', ''):<18} | {bpm:<5} | {item.get('license', 'CC'):<15} | {item.get('mood', '')}")
    print("=" * 90)
    print("  👉 Usage in render:  --music <id> (e.g. --music happy_summer or --music experience_einaudi)\n")


def print_sfx(category=None):
    from video_templates.core.audio import list_audio_items
    items = list_audio_items(kind="sfx", category=category)
    cat_str = f" [Category: {category}]" if category else ""
    print(f"\n💥 Videofy Open-Source SFX & Ambience Library{cat_str} ({len(items)} items):")
    print("=" * 90)
    print(f"  {'ID / Sound Name':<28} | {'Category':<14} | {'Dur':<6} | {'License':<15} | {'Mood / Description'}")
    print("-" * 90)
    for item in items:
        dur = f"{item.get('duration', 0.0):.1f}s" if item.get('duration') else "--"
        print(f"  {item['id']:<28} | {item.get('category', ''):<14} | {dur:<6} | {item.get('license', 'CC0')[:15]:<15} | {item.get('mood', '')}")
    print("=" * 90)
    print("  👉 Usage in render:  --sfx <id> (e.g. --sfx whoosh_fast or --sfx ocean_waves_crashing)\n")


def load_project_file(project_path: Path) -> dict:
    """Parse a YAML or JSON project recipe file."""
    p = Path(project_path).resolve()
    if not p.is_file():
        raise FileNotFoundError(f"Project recipe file not found: {p}")
    
    with open(p, "r", encoding="utf-8") as f:
        if p.suffix.lower() in [".yaml", ".yml"]:
            data = yaml.safe_load(f)
        elif p.suffix.lower() == ".json":
            data = json.load(f)
        else:
            data = yaml.safe_load(f)
            
    if not isinstance(data, dict):
        raise ValueError(f"Invalid recipe format in {p}: expected dictionary/mapping")
        
    data["_project_dir"] = p.parent
    data["_project_path"] = p
    return data


def resolve_project_path(path_val, base_dir=None):
    """Resolve paths relative to base_dir or WORKSPACE_ROOT."""
    if not path_val:
        return None
    p = Path(path_val)
    if p.is_absolute():
        return p
    if base_dir and (base_dir / p).exists():
        return (base_dir / p).resolve()
    return (WORKSPACE_ROOT / p).resolve()


def validate_project(cfg: dict) -> bool:
    """Validate project configuration, verify media paths and shot timings without rendering."""
    print(f"\n📋 Validating Project Recipe: {cfg.get('name', cfg.get('_project_path', 'Unnamed'))}")
    print("=" * 70)
    preset = cfg.get("preset", "cinematic_landscape")
    print(f"  • Preset           : {preset}")
    if preset not in PRESETS:
        print(f"    ❌ Unknown preset '{preset}'. Available: {list(PRESETS.keys())}")
        return False
    
    footage_dir = resolve_project_path(cfg.get("footage_dir") or cfg.get("footage"), cfg.get("_project_dir"))
    print(f"  • Footage Directory: {footage_dir} {'✅' if footage_dir and footage_dir.exists() else '❌ (Not Found)'}")
    
    output_file = resolve_project_path(cfg.get("output_file") or cfg.get("output"), cfg.get("_project_dir"))
    print(f"  • Deliverable Path : {output_file}")
    
    music = cfg.get("music") or cfg.get("music_track")
    sfx = cfg.get("sfx") or cfg.get("sfx_track")
    print(f"  • Audio Pairing    : Music={music}, SFX={sfx}")
    
    shots = cfg.get("shots") or cfg.get("timeline")
    if shots:
        print(f"  • Curated Shots    : {len(shots)} items defined")
        total_planned = 0.0
        missing_count = 0
        for i, s in enumerate(shots):
            if isinstance(s, dict):
                fn = s.get("file") or s.get("filename")
                st = float(s.get("start", 0.0))
                et = float(s.get("end", st + 5.0))
            elif len(s) >= 3:
                fn, st, et = s[:3]
            else:
                continue
            dur = et - st
            total_planned += dur
            
            sp = resolve_project_path(fn, footage_dir)
            if not sp.is_file() and footage_dir:
                matches = list(footage_dir.glob(f"**/{Path(fn).name}"))
                if not matches:
                    print(f"    ⚠️ Shot #{i+1:02d} missing: {fn}")
                    missing_count += 1
        print(f"  • Planned Duration : {total_planned:.1f}s across {len(shots)} cuts")
        if missing_count == 0:
            print("  • Shot Media Check : ✅ All media files verified on disk")
        else:
            print(f"  • Shot Media Check : ⚠️ {missing_count} media files missing")
    
    vox = cfg.get("voiceover")
    if vox:
        speed = vox.get("speed", 0.92) if isinstance(vox, dict) else 0.92
        text = vox.get("text", "") if isinstance(vox, dict) else str(vox)
        phrases = [p.strip() for p in text.split(" | ") if p.strip()]
        print(f"  • Voiceover Script : ✅ {len(phrases)} phrases ({len(text)} chars, speed={speed}x)")
    
    print("=" * 70)
    print("✨ Validation Check Complete!\n")
    return True


def render_project(cfg: dict, args):
    """Execute video template render for a loaded declarative recipe."""
    preset_name = cfg.get("preset", "cinematic_landscape")
    # Command line override if explicitly supplied
    if args.preset and args.preset != "insta_catchy_reel":
        preset_name = args.preset
        
    footage_dir = resolve_project_path(cfg.get("footage_dir") or cfg.get("footage"), cfg.get("_project_dir"))
    output_file = resolve_project_path(cfg.get("output_file") or cfg.get("output"), cfg.get("_project_dir"))
    qc_file = resolve_project_path(cfg.get("qc_file") or cfg.get("qc_sheet") or cfg.get("qc"), cfg.get("_project_dir"))
    
    vox = cfg.get("voiceover")
    vox_text = None
    vox_speed = 0.92
    if isinstance(vox, dict):
        vox_text = vox.get("text")
        vox_speed = float(vox.get("speed", 0.92))
    elif isinstance(vox, str):
        vox_text = vox
    
    # Allow CLI overrides
    if args.voiceover:
        vox_text = args.voiceover
    if args.voiceover_speed != 0.92:
        vox_speed = args.voiceover_speed

    kwargs = {
        "footage_dir": footage_dir,
        "output_file": output_file,
        "qc_file": qc_file,
        "title": cfg.get("title", "CINEMATIC JOURNEY"),
        "subtitle": cfg.get("subtitle", ""),
        "outro_title": cfg.get("outro_title", ""),
        "outro_subtitle": cfg.get("outro_subtitle", ""),
        "handle": cfg.get("handle", "@tamoghna.travels"),
        "lut_name": cfg.get("lut") or cfg.get("lut_name"),
        "grade_preset": cfg.get("grade") or cfg.get("grade_preset", "clean_landscape"),
        "music_track": cfg.get("music") or cfg.get("music_track"),
        "sfx_track": cfg.get("sfx") or cfg.get("sfx_track"),
        "max_duration": cfg.get("max_duration") or cfg.get("duration", 120.0),
        "video_clip_duration": cfg.get("clip_duration", 5.0),
        "black_bars": cfg.get("black_bars", False),
        "smart_crop": cfg.get("smart_crop", False),
        "beat_sync": cfg.get("beat_sync", False),
        "shots": cfg.get("shots") or cfg.get("timeline"),
        "voiceover_text": vox_text,
        "voiceover_speed": vox_speed,
        "accel": args.accel if args.accel != "auto" else cfg.get("accel", "auto")
    }
    
    # Apply explicit CLI overrides if set
    for field in ["title", "subtitle", "outro_title", "outro_subtitle", "handle", "grade", "lut", "music", "sfx"]:
        val = getattr(args, field, None)
        if val is not None:
            if field == "grade":
                kwargs["grade_preset"] = val
            elif field == "lut":
                kwargs["lut_name"] = None if val.lower() == "none" else val
            elif field == "music":
                kwargs["music_track"] = val
            elif field == "sfx":
                kwargs["sfx_track"] = val
            else:
                kwargs[field] = val
                
    if args.duration is not None:
        kwargs["max_duration"] = args.duration
    if args.black_bars:
        kwargs["black_bars"] = True
    if args.smart_crop:
        kwargs["smart_crop"] = True
    if args.beat_sync:
        kwargs["beat_sync"] = True

    print("\n" + "=" * 75)
    print(f"🚀 Executing Declarative Recipe: [{cfg.get('name', output_file.name)}]")
    print(f"🎬 Preset Engine     : {preset_name}")
    print(f"📂 Footage Directory : {footage_dir}")
    print(f"🎯 Output Deliverable: {output_file}")
    print(f"⚡ Acceleration Mode : {kwargs['accel'].upper()}")
    if kwargs.get('shots'):
        print(f"✂️ Curated Sequence  : {len(kwargs['shots'])} planned shots")
    if vox_text:
        print(f"🎙️ Cloned Voiceover : ENABLED ({len(vox_text)} chars, speed={vox_speed:.2f}x)")
    if qc_file:
        print(f"🔍 Visual QC Sheet   : {qc_file}")
    print("=" * 75 + "\n")
    
    render_fn = PRESETS[preset_name]
    res = render_fn(**kwargs)
    print(f"\n🎉 Successfully rendered deliverable: {output_file.name}")
    return res


def main():
    parser = argparse.ArgumentParser(
        description="Videofy Engine CLI - Render high-impact videos with standard templates."
    )
    # Project recipe mode
    parser.add_argument("-c", "--config", "--project", dest="projects", type=str, nargs="*", default=None,
                        help="Path to one or more declarative project recipe files (.yaml or .json)")
    parser.add_argument("--validate", "--dry-run", dest="dry_run", action="store_true",
                        help="Validate project configuration, verify media paths and shot timings without rendering")

    # Interactive / CLI Flags Mode
    parser.add_argument("-p", "--preset", choices=list(PRESETS.keys()), default="insta_catchy_reel",
                        help="Video preset to render (default: insta_catchy_reel)")
    parser.add_argument("-f", "--footage", type=str,
                        help="Path to folder containing raw video and photo footage")
    parser.add_argument("-o", "--output", type=str,
                        help="Output deliverable MP4 path")
    parser.add_argument("--qc", type=str, default=None,
                        help="Optional output path for visual QC contact sheet (.png)")
    
    # Text overlays
    parser.add_argument("--title", type=str, default=None, help="Main title for intro card")
    parser.add_argument("--subtitle", type=str, default=None, help="Subtitle for intro card")
    parser.add_argument("--outro-title", type=str, default=None, help="Title for outro CTA card")
    parser.add_argument("--outro-subtitle", type=str, default=None, help="Subtitle for outro CTA card")
    parser.add_argument("--handle", type=str, default=None, help="Social media handle (e.g. @wanderer)")

    # Timeline & pacing
    parser.add_argument("-d", "--duration", type=float, default=None, help="Target timeline max duration in seconds")
    parser.add_argument("--clip-duration", type=float, default=None, help="Length per video clip in seconds")
    parser.add_argument("--card-duration", type=float, default=None, help="Length per photo Polaroid card in seconds")

    # Grading & audio
    parser.add_argument("--lut", type=str, default=None, help="3D LUT filename or 'none'")
    parser.add_argument("--grade", type=str, default=None, help="Tone curve preset (summer_vibrant, culinary_warm, clean_landscape, moody_contrast, odyssey)")
    parser.add_argument("--music", type=str, default=None, help="Background music filename (in bg_music/) or path")
    parser.add_argument("--sfx", type=str, default=None, help="SFX audio filename (in bg_music/) or path")

    # AI & Hardware Acceleration
    parser.add_argument("--accel", choices=["auto", "nvenc", "qsv", "videotoolbox", "vaapi", "cpu"], default="auto",
                        help="GPU hardware acceleration encoder (default: auto)")
    parser.add_argument("--beat-sync", action="store_true",
                        help="Enable AI musical downbeat synchronization for clip transitions")
    parser.add_argument("--smart-crop", action="store_true",
                        help="Enable AI subject/face tracking for dynamic 9:16 auto-framing")
    parser.add_argument("--voiceover", type=str, default=None,
                        help="Narrative script to synthesize in your personal cloned voice (Qwen3-TTS)")
    parser.add_argument("--voiceover-file", type=str, default=None,
                        help="Path to text file containing narrative voiceover script")
    parser.add_argument("--voiceover-speed", type=float, default=0.92,
                        help="Voiceover speech tempo multiplier (default: 0.92 for contemplative storytelling)")
    parser.add_argument("--black-bars", action="store_true",
                        help="Add top and bottom cinematic black frame bars for clean letterbox text framing")

    # Informational utilities
    parser.add_argument("--list-presets", action="store_true", help="List all available presets and exit")
    parser.add_argument("--list-luts", action="store_true", help="List available 3D LUTs and exit")
    parser.add_argument("--list-music", nargs="?", const="", default=None,
                        help="List available open-source music tracks (optional category filter, e.g. cinematic_epic, travel_upbeat)")
    parser.add_argument("--list-sfx", nargs="?", const="", default=None,
                        help="List available open-source SFX items (optional category filter, e.g. transitions, foley_ui, ambience)")
    parser.add_argument("--download-audio", action="store_true",
                        help="Download & synthesize the complete open-source music and SFX library")
    parser.add_argument("--info", action="store_true", help="Display system hardware acceleration details and exit")

    args = parser.parse_args()

    if args.info:
        print_system_info()
        return

    if args.list_presets:
        print_presets()
        return

    if args.list_luts:
        print_luts()
        return

    if args.list_music is not None:
        print_music(category=args.list_music if args.list_music else None)
        return

    if args.list_sfx is not None:
        print_sfx(category=args.list_sfx if args.list_sfx else None)
        return

    if args.download_audio:
        import subprocess
        print("\n🚀 Executing Automated Open-Source Audio Library Builder...")
        subprocess.run([sys.executable, str(WORKSPACE_ROOT / "download_audio_library.py")], check=True)
        return

    # 1. Project Recipe Execution Mode
    if args.projects:
        for proj_pattern in args.projects:
            # Expand globs if any
            matched = list(Path.cwd().glob(proj_pattern)) or [Path(proj_pattern)]
            for proj_path in matched:
                try:
                    cfg = load_project_file(proj_path)
                    if args.dry_run:
                        validate_project(cfg)
                    else:
                        render_project(cfg, args)
                except Exception as e:
                    print(f"❌ Failed processing project '{proj_path}': {e}", file=sys.stderr)
                    import traceback
                    traceback.print_exc()
                    sys.exit(1)
        return

    # 2. Ad-hoc CLI Flags Execution Mode
    if not args.footage:
        parser.error("Must supply either --project / -c <recipe.yaml> or --footage <dir>.")

    footage_path = Path(args.footage).resolve()
    if not footage_path.exists():
        print(f"❌ Error: Footage folder '{footage_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    # Determine default output file if not specified
    if not args.output:
        stem = footage_path.name.lower().replace(" ", "_")
        args.output = str(WORKSPACE_ROOT / "edit" / f"{stem}_{args.preset}.mp4")

    output_path = Path(args.output).resolve()
    qc_path = Path(args.qc).resolve() if args.qc else None

    kwargs = {
        "footage_dir": footage_path,
        "output_file": output_path,
        "qc_file": qc_path,
    }

    if args.title is not None:
        kwargs["title"] = args.title
    if args.subtitle is not None:
        kwargs["subtitle"] = args.subtitle
    if args.outro_title is not None:
        kwargs["outro_title"] = args.outro_title
    if args.outro_subtitle is not None:
        kwargs["outro_subtitle"] = args.outro_subtitle
    if args.handle is not None:
        kwargs["handle"] = args.handle
    if args.duration is not None:
        kwargs["max_duration"] = args.duration
    if args.clip_duration is not None:
        kwargs["video_clip_duration"] = args.clip_duration
    if args.card_duration is not None and args.preset == "insta_catchy_reel":
        kwargs["photo_card_duration"] = args.card_duration
    if args.lut is not None:
        kwargs["lut_name"] = None if args.lut.lower() == "none" else args.lut
    if args.grade is not None:
        kwargs["grade_preset"] = args.grade
    if args.music is not None:
        kwargs["music_track"] = args.music
    if args.sfx is not None:
        kwargs["sfx_track"] = args.sfx

    # AI & Accel options
    if args.accel != "auto" or True:
        kwargs["accel"] = args.accel
    if args.beat_sync:
        kwargs["beat_sync"] = True
    if args.smart_crop:
        kwargs["smart_crop"] = True
    if args.black_bars:
        kwargs["black_bars"] = True

    # Cloned Voiceover options
    voiceover_text = args.voiceover
    if args.voiceover_file:
        p_vf = Path(args.voiceover_file).resolve()
        if p_vf.is_file():
            voiceover_text = p_vf.read_text(encoding="utf-8").strip()
    if voiceover_text:
        kwargs["voiceover_text"] = voiceover_text
        kwargs["voiceover_speed"] = args.voiceover_speed

    print("\n" + "=" * 70)
    print(f"🚀 Launching Videofy Engine: [{args.preset}]")
    print(f"📂 Footage Directory : {footage_path}")
    print(f"🎯 Output Deliverable: {output_path}")
    print(f"⚡ Acceleration Mode : {args.accel.upper()}")
    if args.beat_sync:
        print("🎵 AI Beat Sync     : ENABLED")
    if args.smart_crop:
        print("🎯 AI Smart Crop    : ENABLED")
    if voiceover_text:
        print(f"🎙️ Cloned Voiceover : ENABLED ({len(voiceover_text)} chars, speed={args.voiceover_speed:.2f}x)")
    if qc_path:
        print(f"🔍 Visual QC Sheet   : {qc_path}")
    print("=" * 70 + "\n")

    render_fn = PRESETS[args.preset]
    try:
        render_fn(**kwargs)
        print("\n" + "🎉" * 3 + f" Render Completed Successfully! Output: {output_path}\n")
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
