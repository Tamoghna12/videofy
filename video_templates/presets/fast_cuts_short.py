"""
fast_cuts_short.py - Preset: Fast Cuts TikTok / Shorts Micro-Reel (9:16 Portrait)
15-20s rapid-fire cuts, beat drops, fast zoom motion, punchy typography,
AI beat-sync, and GPU hardware acceleration.
"""

import shutil
import subprocess
from pathlib import Path

from ..core.conformer import conform_clip
from ..core.grading import get_color_filter
from ..core.overlays import build_timeline_overlays
from ..core.audio import resolve_audio, build_audio_filter
from ..core.accel import get_encoder_args
from ..core.beat_sync import detect_beats, snap_timeline_to_beats
from ..core.qc import generate_contact_sheet
from ..mcp_bridge import validate_deliverable


def render(
    footage_dir,
    output_file,
    qc_file=None,
    title="EXPLORE QUICK",
    subtitle="Fast Travel Hook",
    outro_title="FOLLOW FOR MORE",
    outro_subtitle="Next stop coming soon",
    handle="@quick.shorts",
    lut_name="CINECOLOR_GOLDEN_HOUR.CUBE",
    grade_preset="summer_vibrant",
    music_track="memory_reboot.mp3",
    sfx_track="ocean_waves_crashing.mp3",
    max_duration=18.0,
    video_clip_duration=1.8,
    accel="auto",
    beat_sync=False,
    smart_crop=False,
    **kwargs
):
    footage_dir = Path(footage_dir)
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    tmp_dir = output_file.parent / f"_tmp_{output_file.stem}"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    vids = sorted(list(footage_dir.glob("*.mp4")) + list(footage_dir.glob("*.MP4")))
    if not vids:
        raise ValueError(f"No video files found in {footage_dir}")

    # Optional AI beat detection
    music_file = resolve_audio(music_track) or resolve_audio("memory_reboot.mp3")
    detected_beats = []
    if beat_sync and music_file:
        beat_info = detect_beats(music_file, duration=max_duration, min_interval=0.4)
        detected_beats = beat_info.get("beats", [])

    # Prepare clip list
    clip_count = min(len(vids), int(max_duration / 1.5))
    selected_vids = vids[:clip_count]
    raw_durs = [video_clip_duration] * len(selected_vids)

    if beat_sync and detected_beats:
        planned_durs, _ = snap_timeline_to_beats(raw_durs, detected_beats, tolerance=0.5)
    else:
        planned_durs = raw_durs

    color_vf = get_color_filter(grade_type=grade_preset, lut_name=lut_name)
    timeline_segments = []
    shot_captions = []
    curr_total = 0.0

    for i, v_path in enumerate(selected_vids):
        dur = planned_durs[i]
        if curr_total + dur > max_duration + 0.5:
            break
        seg_out = tmp_dir / f"seg_{i:02d}.mp4"
        conform_clip(
            v_path,
            start=1.0,
            end=1.0 + dur,
            out_path=seg_out,
            target_res="1080x1920",
            fps=24,
            color_filter=color_vf,
            zoom_rate=0.035,
            accel=accel,
            smart_crop=smart_crop
        )
        timeline_segments.append(seg_out)
        shot_captions.append((dur, f"Clip {i+1:02d}"))
        curr_total += dur

    # Concatenate
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

    # Overlays & Audio Mastering
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

    waves_file = resolve_audio(sfx_track, is_sfx=True) or resolve_audio("ocean_waves_crashing.mp3", is_sfx=True)
    audio_vf = build_audio_filter(total_dur, music_volume=1.0, sfx_volume=0.15, target_lufs=-16)

    out_enc_args = get_encoder_args(preference=accel, crf=18, is_segment=False)
    mux_cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-i", str(raw_master),
        "-i", str(music_file),
        "-i", str(waves_file),
        "-filter_complex", f"[0:v]{overlay_vf}[vout];{audio_vf}",
        "-map", "[vout]", "-map", "[aout]",
    ]
    mux_cmd.extend(out_enc_args)
    mux_cmd.extend([
        "-c:a", "aac", "-b:a", "256k",
        "-movflags", "+faststart",
        "-t", f"{total_dur:.2f}",
        str(output_file)
    ])
    subprocess.run(mux_cmd, check=True)

    if qc_file:
        generate_contact_sheet(output_file, qc_file, num_frames=12, aspect="9:16")

    shutil.rmtree(tmp_dir, ignore_errors=True)
    qc_res = validate_deliverable(output_file, expected_aspect="9:16")
    return {
        "output_file": str(output_file),
        "qc_file": str(qc_file) if qc_file else None,
        "qc_validation": qc_res
    }
