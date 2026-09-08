"""
insta_catchy_reel.py - Preset: Instagram Catchy Reel (9:16 Portrait)
Interweaves live video clips + Polaroid photo snapshots with
shutter flashes, top progress bar, lower-thirds, upbeat music,
AI beat-drop synchronization, AI smart-crop, and GPU acceleration.
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
from ..core.accel import get_encoder_args
from ..core.beat_sync import detect_beats, snap_timeline_to_beats
from ..core.voiceover import (
    generate_spaced_story_voiceover,
    generate_voiceover,
    is_voiceover_available
)
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
    photo_card_duration=2.4,
    accel="auto",
    beat_sync=False,
    smart_crop=False,
    voiceover_text=None,
    voiceover_speed=1.15,
    **kwargs
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
    pair_count = max(2, int(max_duration / 7.0))
    selected_vids = vids[:pair_count * 2] if len(vids) >= pair_count * 2 else vids
    selected_imgs = imgs[:pair_count] if len(imgs) >= pair_count else imgs

    # 2. Render Polaroid Cards
    polaroid_items = []
    for i, img_path in enumerate(selected_imgs):
        card_png = cards_dir / f"polaroid_{i:02d}.png"
        tilt = -2.5 if i % 2 == 0 else 2.5
        create_polaroid_card(
            img_path,
            title=img_path.stem.replace("_", " "),
            subtitle=subtitle,
            angle=tilt,
            out_png=card_png
        )

        polaroid_items.append((card_png, img_path))

    # 3. Optional AI Beat-Drop Sync
    music_file = resolve_audio(music_track) or resolve_audio("happy_summer.mp3")
    detected_beats = []
    if beat_sync and music_file:
        print("🎵 Analyzing audio rhythm and downbeats for beat-sync cuts...")
        beat_info = detect_beats(music_file, duration=max_duration)
        detected_beats = beat_info.get("beats", [])
        print(f"   Detected {len(detected_beats)} beat transients (Estimated {beat_info.get('tempo_estimate_bpm')} BPM)")

    # Build sequence of segment durations
    raw_durations = []
    temp_total = 0.0
    v_idx = 0
    p_idx = 0
    actions = [] # ("video", v_idx) or ("photo", p_idx)

    while temp_total < max_duration and (v_idx < len(selected_vids) or p_idx < len(polaroid_items)):
        for _ in range(2 if p_idx < len(polaroid_items) else 1):
            if v_idx < len(selected_vids) and temp_total < max_duration:
                actions.append(("video", selected_vids[v_idx]))
                raw_durations.append(video_clip_duration)
                temp_total += video_clip_duration
                v_idx += 1

        if p_idx < len(polaroid_items) and temp_total < max_duration:
            actions.append(("photo", polaroid_items[p_idx]))
            raw_durations.append(photo_card_duration)
            temp_total += photo_card_duration
            p_idx += 1

    if v_idx < len(selected_vids):
        actions.append(("video", selected_vids[v_idx]))
        raw_durations.append(min(4.5, video_clip_duration))

    if beat_sync and detected_beats:
        planned_durations, _ = snap_timeline_to_beats(raw_durations, detected_beats)
    else:
        planned_durations = raw_durations

    # 4. Render Conformed Timeline Segments
    color_vf = get_color_filter(grade_type=grade_preset, lut_name=lut_name)
    timeline_segments = []
    shot_captions = []
    curr_total = 0.0

    for seg_idx, (act_type, act_data) in enumerate(actions):
        dur = planned_durations[seg_idx]
        seg_out = tmp_dir / f"seg_{seg_idx:02d}.mp4"

        if act_type == "video":
            v_path = act_data
            conform_clip(
                v_path,
                start=1.5,
                end=1.5 + dur,
                out_path=seg_out,
                target_res="1080x1920",
                fps=24,
                color_filter=color_vf,
                accel=accel,
                smart_crop=smart_crop
            )
            timeline_segments.append(seg_out)
            shot_captions.append((dur, f"Exploring {footage_dir.name.replace('_', ' ').title()}"))
        else:
            c_png, orig_img = act_data
            render_photo_motion_segment(
                c_png,
                orig_img,
                duration=dur,
                out_video=seg_out,
                canvas_res="1080x1920",
                fps=24
            )
            timeline_segments.append(seg_out)
            shot_captions.append((dur, f"{subtitle}"))

        curr_total += dur

    # 5. Concatenate
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

    # 6. Voiceover & Kinetic Typography Synthesis
    vox_data = None
    if voiceover_text and is_voiceover_available():
        vox_dir = tmp_dir / "voiceover"
        vox_speed = voiceover_speed if voiceover_speed != 1.15 else 0.92
        try:
            vox_data = generate_spaced_story_voiceover(
                narration=voiceover_text,
                total_duration=total_dur,
                output_dir=vox_dir,
                speed=vox_speed,
                font_size=50
            )
        except Exception as e:
            print(f"⚠️ Spaced voiceover synthesis failed, using single-block fallback: {e}")
            vox_path = tmp_dir / "voiceover.wav"
            vox_info = generate_voiceover(voiceover_text, output_path=vox_path, speed=vox_speed)
            vox_data = {
                "audio_file": vox_info["audio_file"],
                "subtitles_ass": None,
                "ducking_intervals": None,
                "duration": vox_info["duration"]
            }

    # 7. Overlays & Audio Mastering
    # Suppress generic shot captions when kinetic voiceover subtitles are active to prevent visual clash
    display_shot_captions = [] if (vox_data and vox_data.get("subtitles_ass")) else shot_captions
    overlay_vf = build_timeline_overlays(
        total_dur,
        shot_captions=display_shot_captions,
        intro_title=title,
        intro_subtitle=subtitle,
        outro_title=outro_title,
        outro_subtitle=outro_subtitle,
        handle=handle,
        aspect="9:16"
    )

    # Burn kinetic ASS highlighted subtitles
    if vox_data and vox_data.get("subtitles_ass"):
        ass_path = str(vox_data["subtitles_ass"]).replace("\\", "/").replace(":", "\\:")
        overlay_vf = f"{overlay_vf},ass='{ass_path}'"

    waves_file = resolve_audio(sfx_track, is_sfx=True) or resolve_audio("ocean_waves_crashing.mp3", is_sfx=True)
    if vox_data and vox_data.get("ducking_intervals"):
        audio_vf = build_audio_filter(
            total_dur,
            music_volume=1.0,
            sfx_volume=0.20,
            target_lufs=-16,
            has_sfx=True,
            ducking_intervals=vox_data["ducking_intervals"],
            voiceover_is_timeline=True
        )
    else:
        vox_dur = vox_data.get("duration") if vox_data else None
        audio_vf = build_audio_filter(
            total_dur,
            music_volume=1.0,
            sfx_volume=0.20,
            target_lufs=-16,
            has_sfx=True,
            voiceover_duration=vox_dur,
            voiceover_start=1.5
        )

    # Output encoding with GPU acceleration
    out_enc_args = get_encoder_args(preference=accel, crf=18, is_segment=False)

    mux_cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-i", str(raw_master),
        "-i", str(music_file),
        "-i", str(waves_file),
    ]
    if vox_data:
        mux_cmd.extend(["-i", str(vox_data["audio_file"])])

    mux_cmd.extend([
        "-filter_complex", f"[0:v]{overlay_vf}[vout];{audio_vf}",
        "-map", "[vout]", "-map", "[aout]",
    ])
    mux_cmd.extend(out_enc_args)
    mux_cmd.extend([
        "-c:a", "aac", "-b:a", "256k",
        "-movflags", "+faststart",
        "-t", f"{total_dur:.2f}",
        str(output_file)
    ])
    subprocess.run(mux_cmd, check=True)

    # 7. QC Contact Sheet
    if qc_file:
        generate_contact_sheet(output_file, qc_file, num_frames=12, aspect="9:16")

    # Cleanup tmp
    shutil.rmtree(tmp_dir, ignore_errors=True)

    # 8. Deliverable verification
    qc_res = validate_deliverable(output_file, expected_aspect="9:16")
    return {
        "output_file": str(output_file),
        "qc_file": str(qc_file) if qc_file else None,
        "qc_validation": qc_res
    }
