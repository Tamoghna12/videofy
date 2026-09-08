"""
insta_catchy_reel.py - Preset: Instagram Catchy Reel (9:16 Portrait)
Interweaves live video clips + Polaroid photo snapshots with
shutter flashes, top progress bar, lower-thirds, and upbeat music.
"""

import shutil
import subprocess
from pathlib import Path

from ..core.conformer import conform_clip
from ..core.polaroids import create_polaroid_card, render_photo_motion_segment
from ..core.grading import get_color_filter
from ..core.overlays import build_timeline_overlays
from ..core.audio import resolve_audio, build_audio_filter
from ..core.qc import generate_contact_sheet
from ..mcp_bridge import validate_deliverable


def render(
    footage_dir,
    output_file,
    qc_file=None,
    title="EXPLORE THE COAST",
    subtitle="WILD ADVENTURES",
    outro_title="UNFORGETTABLE JOURNEY",
    outro_subtitle="Save this for your next trip 📍",
    handle="@travel.explore",
    lut_name="CINECOLOR_GOLDEN_HOUR.CUBE",
    grade_preset="summer_vibrant",
    music_track="happy_summer.mp3",
    sfx_track="ocean_waves_crashing.mp3",
    max_duration=60.0,
    video_clip_duration=4.5,
    photo_card_duration=2.4
):
    footage_dir = Path(footage_dir)
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    tmp_dir = output_file.parent / f"_tmp_{output_file.stem}"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)
    cards_dir = tmp_dir / "cards"
    cards_dir.mkdir(exist_ok=True)

    # 1. Discover Media
    vids = sorted(list(footage_dir.glob("*.mp4")) + list(footage_dir.glob("*.MP4")))
    imgs = sorted(list(footage_dir.glob("*.jpg")) + list(footage_dir.glob("*.JPG")))

    if not vids:
        raise ValueError(f"No video files found in {footage_dir}")

    # Determine timeline count based on max_duration
    # Average pair (video + photo) is ~6.9s
    pair_count = max(2, int(max_duration / 7.0))
    selected_vids = vids[:pair_count * 2] if len(vids) >= pair_count * 2 else vids
    selected_imgs = imgs[:pair_count] if len(imgs) >= pair_count else imgs

    # 2. Build Polaroid Cards
    polaroid_items = []
    angles = [-2.4, 2.6, -1.8, 2.2, -2.8, 1.9, -2.0, 2.5]
    for idx, img_path in enumerate(selected_imgs):
        card_png = cards_dir / f"card_{idx:02d}.png"
        angle = angles[idx % len(angles)]
        card_title = img_path.stem.replace("_", " ").upper()
        if len(card_title) > 22:
            card_title = title.upper()
        create_polaroid_card(
            img_path,
            title=card_title,
            subtitle=subtitle,
            angle=angle,
            out_png=card_png
        )
        polaroid_items.append((card_png, img_path))

    # 3. Conform Timeline Segments
    color_vf = get_color_filter(grade_type=grade_preset, lut_name=lut_name)
    timeline_segments = []
    shot_captions = []
    curr_total = 0.0

    v_idx = 0
    p_idx = 0
    seg_counter = 0

    while curr_total < max_duration and (v_idx < len(selected_vids) or p_idx < len(polaroid_items)):
        # Add 1-2 videos
        for _ in range(2 if p_idx < len(polaroid_items) else 1):
            if v_idx < len(selected_vids) and curr_total < max_duration:
                v_path = selected_vids[v_idx]
                seg_out = tmp_dir / f"seg_{seg_counter:02d}.mp4"
                dur = min(video_clip_duration, max_duration - curr_total)
                conform_clip(v_path, start=1.5, end=1.5 + dur, out_path=seg_out, target_res="1080x1920", fps=24, color_filter=color_vf)
                timeline_segments.append(seg_out)
                shot_captions.append((dur, f"Exploring {footage_dir.name.replace('_', ' ').title()}"))
                curr_total += dur
                v_idx += 1
                seg_counter += 1

        # Add 1 photo card
        if p_idx < len(polaroid_items) and curr_total < max_duration:
            c_png, orig_img = polaroid_items[p_idx]
            seg_out = tmp_dir / f"seg_{seg_counter:02d}.mp4"
            dur = min(photo_card_duration, max_duration - curr_total)
            render_photo_motion_segment(c_png, orig_img, duration=dur, out_video=seg_out, canvas_res="1080x1920", fps=24)
            timeline_segments.append(seg_out)
            shot_captions.append((dur, f"{subtitle}"))
            curr_total += dur
            p_idx += 1
            seg_counter += 1

    # Ensure reel finishes with a scenic video clip for clean outro presentation
    if v_idx < len(selected_vids):
        v_path = selected_vids[v_idx]
        seg_out = tmp_dir / f"seg_{seg_counter:02d}.mp4"
        dur = min(4.5, video_clip_duration)
        conform_clip(v_path, start=2.0, end=2.0 + dur, out_path=seg_out, target_res="1080x1920", fps=24, color_filter=color_vf)
        timeline_segments.append(seg_out)
        shot_captions.append((dur, f"Exploring {footage_dir.name.replace('_', ' ').title()}"))
        curr_total += dur
        v_idx += 1
        seg_counter += 1


    # 4. Concatenate
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

    # 5. Overlays & Audio Mastering
    overlay_vf = build_timeline_overlays(
        total_dur,
        shot_captions=shot_captions,
        intro_title=title,
        intro_subtitle=subtitle,
        outro_title=outro_title,
        outro_subtitle=outro_subtitle,
        handle=handle,
        aspect="9:16"
    )

    music_file = resolve_audio(music_track) or resolve_audio("happy_summer.mp3")
    waves_file = resolve_audio(sfx_track, is_sfx=True) or resolve_audio("ocean_waves_crashing.mp3", is_sfx=True)
    audio_vf = build_audio_filter(total_dur, music_volume=1.0, sfx_volume=0.20, target_lufs=-16)

    mux_cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-i", str(raw_master),
        "-i", str(music_file),
        "-i", str(waves_file),
        "-filter_complex", f"[0:v]{overlay_vf}[vout];{audio_vf}",
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "256k",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-t", f"{total_dur:.2f}",
        str(output_file)
    ]
    subprocess.run(mux_cmd, check=True)

    # 6. QC Contact Sheet
    if qc_file:
        generate_contact_sheet(output_file, qc_file, num_frames=12, aspect="9:16")

    # Cleanup tmp
    shutil.rmtree(tmp_dir)

    # 7. Deliverable verification
    qc_res = validate_deliverable(output_file, expected_aspect="9:16")
    return {
        "output_file": str(output_file),
        "qc_file": str(qc_file) if qc_file else None,
        "qc_validation": qc_res
    }
