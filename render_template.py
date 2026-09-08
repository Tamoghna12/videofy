#!/usr/bin/env python3
"""
render_template.py - Unified Command-Line Interface for Video Template Production.

Enables 1-click batch rendering of high-impact videos (Insta Reels, Cinematic Widescreen,
Lifestyle Vlogs, Fast TikTok Shorts) with multi-vendor GPU acceleration, AI beat-sync,
and AI subject auto-framing.
"""

import argparse
import sys
from pathlib import Path

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


def main():
    parser = argparse.ArgumentParser(
        description="Videofy Engine CLI - Render high-impact videos with standard templates."
    )
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
    parser.add_argument("--grade", type=str, default=None, help="Tone curve preset (summer_vibrant, culinary_warm, clean_landscape, moody_contrast)")
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

    if not args.footage:
        parser.error("The --footage argument is required unless using --list-presets, --list-luts, --list-music, --list-sfx, --download-audio, or --info.")

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
