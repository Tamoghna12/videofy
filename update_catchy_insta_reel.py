#!/usr/bin/env python3
"""
update_catchy_insta_reel.py - Update Catchy Instagram Reel (Yorkshire Road Trip)
Applies the standardized cinematic letterbox format, grounded emotional voiceover,
and real-time kinetic gold highlighted subtitles.
"""

import sys
import shutil
import subprocess
from pathlib import Path

WORKSPACE_ROOT = Path("/home/tamoghna/Documents/Video_editing")
sys.path.insert(0, str(WORKSPACE_ROOT))

from video_templates.core.conformer import conform_clip
from video_templates.core.grading import get_color_filter
from video_templates.core.overlays import build_timeline_overlays
from video_templates.core.audio import resolve_audio, build_audio_filter
from video_templates.core.accel import get_encoder_args
from video_templates.core.qc import generate_contact_sheet
from video_templates.core.polaroids import create_polaroid_card, render_photo_motion_segment
from video_templates.core.voiceover import generate_spaced_story_voiceover, is_voiceover_available

OUTPUT_FILE = WORKSPACE_ROOT / "edit/reels_9x16/catchy_insta_reel_9x16.mp4"
QC_FILE = WORKSPACE_ROOT / "edit/verify/qc_sheet_insta_reel.png"

TITLE = "YORKSHIRE ROAD TRIP"
SUBTITLE = "YORK • SCARBOROUGH • WHITBY"
OUTRO_TITLE = "EXPLORE YORKSHIRE"
OUTRO_SUBTITLE = "Save this for your road trip 📍"

VOICEOVER_TEXT = (
    "Winding down through the Yorkshire moors, as the salt air announces the open sea. | "
    "From the grandeur of York's ancient Minster to the quiet shadows of centuries-old stone. | "
    "Every road in Yorkshire carries a memory... of tides, cobblestones, and the open horizon."
)

TIMELINE_RECIPE = [
    ("video", "raw_footage/whitby/20260906_105056.mp4", 1.5, 5.5, "Country road towards the coast"),
    ("video", "raw_footage/scarboro/20260905_160428.mp4", 3.0, 7.0, "Coastal cliff approach"),
    ("photo", "assets/photos/scarborough_bay.jpg", "SCARBOROUGH BAY", "Queen of the Yorkshire Coast", -2.5, 2.6),
    ("video", "raw_footage/scarboro/20260905_184406.mp4", 29.0, 33.5, "Scarborough seaside promenade"),
    ("video", "raw_footage/york/day1_part1/20260903_121155.mp4", 2.0, 6.0, "Arriving at York Station"),
    ("photo", "assets/photos/york_shambles.jpg", "THE SHAMBLES", "Historic Medieval York", 2.0, 2.6),
    ("video", "raw_footage/york/day1_part2/20260903_183008.mp4", 4.0, 8.5, "York Minster Gothic facade"),
    ("video", "raw_footage/whitby/20260906_134022.mp4", 12.0, 16.0, "Crossing high above Whitby harbour"),
    ("photo", "assets/photos/whitby_abbey.jpg", "WHITBY ABBEY", "Dramatic Coastal Ruins", -1.8, 2.6),
    ("video", "raw_footage/whitby/20260906_154424.mp4", 0.5, 4.5, "Open moors highway journey"),
]


def main():
    print("=" * 80)
    print("🎬 UPDATING CATCHY INSTA REEL: YORKSHIRE ROAD TRIP (CINEMATIC LETTERBOX FORMAT)")
    print("=" * 80)

    tmp_dir = OUTPUT_FILE.parent / f"_tmp_{OUTPUT_FILE.stem}"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    color_vf = get_color_filter(grade_type="clean_landscape", lut_name="CINECOLOR_GOLDEN_HOUR.CUBE")
    timeline_segments = []
    seg_idx = 0

    print("\n[1/4] Conforming video segments and rendering Polaroid motion cards...")
    for item in TIMELINE_RECIPE:
        item_type = item[0]
        seg_out = tmp_dir / f"seg_{seg_idx:02d}.mp4"

        if item_type == "video":
            _, rel_path, st, et, caption = item
            src_path = WORKSPACE_ROOT / rel_path
            dur = et - st
            conform_clip(
                src_path,
                start=st,
                end=et,
                out_path=seg_out,
                target_res="1080x1920",
                fps=24,
                color_filter=color_vf,
                zoom_rate=0.015,
                accel="auto"
            )
            timeline_segments.append(seg_out)
        elif item_type == "photo":
            _, photo_rel, card_title, card_sub, angle, dur = item
            src_photo = WORKSPACE_ROOT / photo_rel
            card_png = tmp_dir / f"card_{seg_idx:02d}.png"
            create_polaroid_card(
                src_photo,
                title=card_title,
                subtitle=card_sub,
                angle=angle,
                out_png=card_png,
                canvas_size=(1080, 1920)
            )
            render_photo_motion_segment(
                card_png,
                src_photo,
                duration=dur,
                out_video=seg_out,
                canvas_res="1080x1920",
                fps=24
            )
            timeline_segments.append(seg_out)

        seg_idx += 1

    # Concatenate segments
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
    print(f"\n[2/4] Raw Master Assembled: {total_dur:.2f}s across {len(timeline_segments)} cuts.")

    # Voiceover & Kinetic ASS Typography
    print("\n[3/4] Synthesizing Grounded Voiceover & Kinetic Gold ASS Subtitles...")
    vox_dir = tmp_dir / "voiceover"
    vox_data = generate_spaced_story_voiceover(
        narration=VOICEOVER_TEXT,
        total_duration=total_dur,
        output_dir=vox_dir,
        speed=0.92,
        font_size=40,
        margin_v=75,
        play_res_x=1080,
        play_res_y=1920,
        margin_lr=80
    )

    # Overlays (Top & Bottom Matte Bars, Gold Hairline, Outro)
    overlay_vf = build_timeline_overlays(
        total_dur,
        shot_captions=[],
        intro_title=TITLE,
        intro_subtitle=SUBTITLE,
        outro_title=OUTRO_TITLE,
        outro_subtitle=OUTRO_SUBTITLE,
        handle="@yorkshire.travels",
        aspect="9:16",
        black_bars=True
    )

    if vox_data and vox_data.get("subtitles_ass"):
        ass_path = str(vox_data["subtitles_ass"]).replace("\\", "/").replace(":", "\\:")
        overlay_vf = f"{overlay_vf},ass='{ass_path}'"

    music_file = resolve_audio("solas_jamie_duffy") or resolve_audio("experience_einaudi.mp3")
    waves_file = resolve_audio("ocean_waves_crashing.mp3", is_sfx=True)

    audio_vf = build_audio_filter(
        total_dur,
        music_volume=1.0,
        sfx_volume=0.18,
        target_lufs=-16,
        has_sfx=True,
        ducking_intervals=vox_data["ducking_intervals"],
        voiceover_is_timeline=True
    )

    print("\n[4/4] Encoding Final Cinematic Master via NVENC & Mastering Audio...")
    out_enc_args = get_encoder_args(preference="auto", crf=18, is_segment=False)
    mux_cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-i", str(raw_master),
        "-i", str(music_file),
        "-i", str(waves_file),
        "-i", str(vox_data["audio_file"]),
        "-filter_complex", f"[0:v]{overlay_vf}[vout];{audio_vf}",
        "-map", "[vout]", "-map", "[aout]"
    ]
    mux_cmd.extend(out_enc_args)
    mux_cmd.extend([
        "-c:a", "aac", "-b:a", "320k",
        "-movflags", "+faststart",
        "-t", f"{total_dur:.2f}",
        str(OUTPUT_FILE)
    ])
    subprocess.run(mux_cmd, check=True)

    # Update backward-compatible symlink in edit/
    symlink_path = WORKSPACE_ROOT / "edit" / OUTPUT_FILE.name
    if symlink_path.is_symlink() or symlink_path.exists():
        symlink_path.unlink()
    symlink_path.symlink_to(f"reels_9x16/{OUTPUT_FILE.name}")

    # Generate Visual QC Contact Sheet
    generate_contact_sheet(OUTPUT_FILE, QC_FILE, num_frames=12, aspect="9:16")
    shutil.rmtree(tmp_dir, ignore_errors=True)

    print("\n" + "=" * 80)
    print(f"🎉 CATCHY INSTA REEL SUCCESSFULLY UPDATED: {OUTPUT_FILE.name}")
    print(f"🔍 QC Contact Sheet: {QC_FILE.name}")
    print("=" * 80)


if __name__ == "__main__":
    main()
