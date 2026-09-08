#!/usr/bin/env python3
"""
create_york_detailed_reels.py - Detailed 9:16 Portrait Reels for York Day 1 (Parts 1 & 2).

Reel 1 (day1_part1): Train Arrival, Victorian Glass Canopy & Riverside Hotel (~48s)
Reel 2 (day1_part2): The Shambles, York Minster & Medieval Charm (~46s)
"""

import shutil
import subprocess
import sys
from pathlib import Path

# Workspace setup
WORKSPACE_ROOT = Path(__file__).resolve().parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from video_templates.core.conformer import conform_clip
from video_templates.core.grading import get_color_filter
from video_templates.core.overlays import build_timeline_overlays
from video_templates.core.audio import resolve_audio, build_audio_filter
from video_templates.core.qc import generate_contact_sheet
from video_templates.mcp_bridge import validate_deliverable


def render_york_part1():
    print("\n" + "=" * 75)
    print("🎬 RENDERING REEL 1: York Day 1 Part 1 - Arrival, Grand Station & Riverside")
    print("=" * 75)

    footage_dir = WORKSPACE_ROOT / "raw_footage" / "york" / "day1_part1"
    output_file = WORKSPACE_ROOT / "edit" / "york_day1_part1_arrival_reel.mp4"
    qc_file = WORKSPACE_ROOT / "edit" / "verify" / "qc_sheet_york_day1_part1.png"
    tmp_dir = output_file.parent / "_tmp_york_part1"

    if output_file.exists():
        val = validate_deliverable(output_file, expected_aspect="9:16")
        if val.get("valid"):
            print(f"Part 1 deliverable already exists: {output_file}")
            print(f"QC Status: {val}")
            print("Generating 12-frame visual contact sheet...")
            generate_contact_sheet(output_file, qc_file, num_frames=12, aspect="9:16")
            print(f"✅ QC Sheet Saved: {qc_file}")
            return output_file

    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    # 1. Selected Clips & Storyline
    # (src_name, start_sec, duration_sec, caption_text)
    clips_plan = [
        ("20260903_114125.mp4", 4.0, 3.8, "En Route to Historic York"),
        ("20260903_114436.mp4", 0.0, 2.8, "Arriving at York Platform"),
        ("20260903_120710.mp4", 0.5, 3.2, "York Railway Station"),
        ("20260903_120932.mp4", 3.0, 4.5, "Iconic Arched Glass Canopy"),
        ("20260903_121155.mp4", 1.5, 4.2, "Victorian Architectural Marvel"),
        ("20260903_121225.mp4", 1.0, 3.5, "Stepping into Ancient York"),
        ("20260903_131339.mp4", 1.0, 4.2, "River Ouse Riverside Stroll"),
        ("20260903_131536.mp4", 2.0, 3.8, "Hampton by Hilton York"),
        ("20260903_132104.mp4", 1.0, 3.8, "Keycard Unlock & Room Tour"),
        ("20260903_132120.mp4", 1.5, 4.5, "Cozy Modern City Reset"),
        ("20260903_141659.mp4", 3.0, 5.5, "Great British Railway Heritage"),
    ]

    color_vf = get_color_filter(grade_type="summer_vibrant", lut_name="CINECOLOR_GOLDEN_HOUR.CUBE")

    timeline_segments = []
    shot_captions = []

    for i, (fname, start, dur, cap) in enumerate(clips_plan):
        src = footage_dir / fname
        if not src.exists():
            print(f"Warning: {src} missing, skipping...")
            continue
        seg_out = tmp_dir / f"seg_{i:02d}.mp4"
        print(f"  [{i+1:02d}/{len(clips_plan)}] Conforming {fname} ({dur:.1f}s) -> '{cap}'")
        conform_clip(
            src,
            start=start,
            end=start + dur,
            out_path=seg_out,
            target_res="1080x1920",
            fps=24,
            color_filter=color_vf,
            zoom_rate=0.018
        )
        timeline_segments.append(seg_out)
        shot_captions.append((dur, cap))

    # 2. Concat video stream
    concat_txt = tmp_dir / "concat_list.txt"
    concat_txt.write_text("".join(f"file '{p.resolve()}'\n" for p in timeline_segments))
    raw_master = tmp_dir / "raw_master.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_txt),
        "-c", "copy",
        str(raw_master)
    ], check=True)

    dur_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(raw_master)]
    total_dur = float(subprocess.check_output(dur_cmd).strip())
    print(f"\nTimeline Assembled: {total_dur:.2f}s across {len(timeline_segments)} shots.")

    # 3. Motion Overlays & Typography
    overlay_vf = build_timeline_overlays(
        total_duration=total_dur,
        shot_captions=shot_captions,
        intro_title="YORK: DAY 1",
        intro_subtitle="Train Arrival & Riverside Hotel",
        outro_title="YORK: DAY 1",
        outro_subtitle="Save this for your York itinerary 📍",
        handle="@tamoghna.travels",
        aspect="9:16"
    )

    # 4. Audio Mastering (EBU R128 -16 LUFS)
    music_file = resolve_audio("solas_jamie_duffy.mp3") or resolve_audio("happy_summer.mp3")
    train_sfx = resolve_audio("train_rolling_ambience.mp3", is_sfx=True)

    audio_vf = build_audio_filter(total_dur, music_volume=0.95, sfx_volume=0.18, target_lufs=-16)

    # 5. Final Render
    print("Muxing overlays and mastering audio to broadcast standard...")
    render_cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-i", str(raw_master),
        "-i", str(music_file),
        "-i", str(train_sfx),
        "-filter_complex", f"[0:v]{overlay_vf}[vout];{audio_vf}",
        "-map", "[vout]",
        "-map", "[aout]",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "256k",
        "-ar", "48000",
        "-t", f"{total_dur:.3f}",
        str(output_file)
    ]
    subprocess.run(render_cmd, check=True)
    print(f"✅ Deliverable Rendered: {output_file}")

    # 6. QC Validation & Contact Sheet
    val = validate_deliverable(output_file, expected_aspect="9:16")
    print(f"QC Status: {val}")

    print("Generating 12-frame visual contact sheet...")
    generate_contact_sheet(output_file, qc_file, num_frames=12, cols=4)
    print(f"✅ QC Sheet Saved: {qc_file}")

    shutil.rmtree(tmp_dir, ignore_errors=True)
    return output_file


def render_york_part2():
    print("\n" + "=" * 75)
    print("🎬 RENDERING REEL 2: York Day 1 Part 2 - The Shambles & York Minster")
    print("=" * 75)

    footage_dir = WORKSPACE_ROOT / "raw_footage" / "york" / "day1_part2"
    output_file = WORKSPACE_ROOT / "edit" / "york_day1_part2_medieval_reel.mp4"
    qc_file = WORKSPACE_ROOT / "edit" / "verify" / "qc_sheet_york_day1_part2.png"
    tmp_dir = output_file.parent / "_tmp_york_part2"

    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    # 1. Selected Clips & Storyline
    clips_plan = [
        ("20260903_174049.mp4", 0.5, 3.8, "Käthe Wohlfahrt Christmas Shop"),
        ("20260903_174058.mp4", 2.0, 4.2, "Mulberry Hall - Est. 1434"),
        ("20260903_174511.mp4", 1.5, 4.2, "Historic High Street Stroll"),
        ("20260903_181254.mp4", 4.0, 5.5, "The Shambles (Medieval Alley)"),
        ("20260903_183008.mp4", 3.0, 5.8, "York Minster Gothic Cathedral"),
        ("20260903_184627.mp4", 0.5, 4.0, "Lendal Bridge over River Ouse"),
        ("20260903_184645.mp4", 1.5, 4.2, "Peaceful Evening by the Ouse"),
        ("20260905_105339.mp4", 1.0, 4.5, "Living History in Every Corner"),
        ("20260905_115934.mp4", 1.5, 5.5, "Exploring Yorkshire Heartlands"),
    ]

    # Kodak 2383 D65 print film emulation
    color_vf = get_color_filter(grade_type="clean_landscape", lut_name="Rec709 Kodak 2383 D65.cube")

    timeline_segments = []
    shot_captions = []

    for i, (fname, start, dur, cap) in enumerate(clips_plan):
        src = footage_dir / fname
        if not src.exists():
            print(f"Warning: {src} missing, skipping...")
            continue
        seg_out = tmp_dir / f"seg_{i:02d}.mp4"
        print(f"  [{i+1:02d}/{len(clips_plan)}] Conforming {fname} ({dur:.1f}s) -> '{cap}'")
        conform_clip(
            src,
            start=start,
            end=start + dur,
            out_path=seg_out,
            target_res="1080x1920",
            fps=24,
            color_filter=color_vf,
            zoom_rate=0.016
        )
        timeline_segments.append(seg_out)
        shot_captions.append((dur, cap))

    # 2. Concat video stream
    concat_txt = tmp_dir / "concat_list.txt"
    concat_txt.write_text("".join(f"file '{p.resolve()}'\n" for p in timeline_segments))
    raw_master = tmp_dir / "raw_master.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_txt),
        "-c", "copy",
        str(raw_master)
    ], check=True)

    dur_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(raw_master)]
    total_dur = float(subprocess.check_output(dur_cmd).strip())
    print(f"\nTimeline Assembled: {total_dur:.2f}s across {len(timeline_segments)} shots.")

    # 3. Motion Overlays & Typography
    overlay_vf = build_timeline_overlays(
        total_duration=total_dur,
        shot_captions=shot_captions,
        intro_title="MEDIEVAL YORK",
        intro_subtitle="The Shambles & York Minster",
        outro_title="MEDIEVAL YORK",
        outro_subtitle="Follow for more British journeys 📍",
        handle="@tamoghna.travels",
        aspect="9:16"
    )

    # 4. Audio Mastering (EBU R128 -16 LUFS)
    music_file = resolve_audio("experience_einaudi.mp3") or resolve_audio("debussy_clair_de_lune.mp3")
    sfx_file = resolve_audio("church_bells_cathedral.mp3", is_sfx=True) or resolve_audio("gentle_rain_ambience.mp3", is_sfx=True)

    audio_vf = build_audio_filter(total_dur, music_volume=0.95, sfx_volume=0.18, target_lufs=-16)

    # 5. Final Render
    print("Muxing overlays and mastering audio to broadcast standard...")
    render_cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-i", str(raw_master),
        "-i", str(music_file),
        "-i", str(sfx_file),
        "-filter_complex", f"[0:v]{overlay_vf}[vout];{audio_vf}",
        "-map", "[vout]",
        "-map", "[aout]",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "256k",
        "-ar", "48000",
        "-t", f"{total_dur:.3f}",
        str(output_file)
    ]
    subprocess.run(render_cmd, check=True)
    print(f"✅ Deliverable Rendered: {output_file}")

    # 6. QC Validation & Contact Sheet
    val = validate_deliverable(output_file, expected_aspect="9:16")
    print(f"QC Status: {val}")

    print("Generating 12-frame visual contact sheet...")
    generate_contact_sheet(output_file, qc_file, num_frames=12, aspect="9:16")
    print(f"✅ QC Sheet Saved: {qc_file}")

    shutil.rmtree(tmp_dir, ignore_errors=True)
    return output_file


def main():
    out1 = render_york_part1()
    out2 = render_york_part2()
    print("\n" + "🎉" * 5)
    print("BOTH YORK DETAILED REELS RENDERED SUCCESSFULLY!")
    print(f"Reel 1: {out1}")
    print(f"Reel 2: {out2}")
    print("🎉" * 5 + "\n")


if __name__ == "__main__":
    main()
