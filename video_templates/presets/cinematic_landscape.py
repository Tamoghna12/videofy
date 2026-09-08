"""
cinematic_landscape.py - Preset: 16:9 Widescreen Film Emulation
Applies Kodak 2383 D65 print film emulation, slow Ken Burns push-in,
cinematic title cards, and orchestral crescendos with GPU acceleration.
"""

import shutil
import subprocess
from pathlib import Path

from ..core.conformer import conform_clip
from ..core.grading import get_color_filter
from ..core.overlays import build_timeline_overlays
from ..core.audio import resolve_audio, build_audio_filter
from ..core.accel import get_encoder_args
from ..core.qc import generate_contact_sheet
from ..mcp_bridge import validate_deliverable


def render(
    footage_dir,
    output_file,
    qc_file=None,
    title="CINEMATIC JOURNEY",
    subtitle="YORKSHIRE & THE ATLANTIC",
    outro_title="DISCOVER THE LANDSCAPE",
    outro_subtitle="Full 4K Widescreen Edition",
    handle="@landscape.cinematic",
    lut_name="Rec709 Kodak 2383 D65.cube",
    grade_preset="clean_landscape",
    music_track="experience_einaudi.mp3",
    sfx_track="ocean_waves_crashing.mp3",
    max_duration=60.0,
    video_clip_duration=5.5,
    accel="auto",
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

    color_vf = get_color_filter(grade_type=grade_preset, lut_name=lut_name)
    timeline_segments = []
    shot_captions = []
    curr_total = 0.0

    v_idx = 0
    seg_counter = 0

    while curr_total < max_duration and v_idx < len(vids):
        v_path = vids[v_idx]
        seg_out = tmp_dir / f"seg_{seg_counter:02d}.mp4"
        dur = min(video_clip_duration, max_duration - curr_total)
        conform_clip(
            v_path,
            start=1.5,
            end=1.5 + dur,
            out_path=seg_out,
            target_res="1920x1080",
            fps=24,
            color_filter=color_vf,
            zoom_rate=0.018,
            accel=accel,
            smart_crop=smart_crop
        )
        timeline_segments.append(seg_out)
        shot_captions.append((dur, f"Scene {seg_counter+1:02d}"))
        curr_total += dur
        v_idx += 1
        seg_counter += 1

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
        aspect="16:9"
    )

    music_file = resolve_audio(music_track) or resolve_audio("experience_einaudi.mp3")
    waves_file = resolve_audio(sfx_track, is_sfx=True) or resolve_audio("ocean_waves_crashing.mp3", is_sfx=True)
    audio_vf = build_audio_filter(total_dur, music_volume=0.95, sfx_volume=0.20, target_lufs=-14)

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
        "-c:a", "aac", "-b:a", "320k",
        "-movflags", "+faststart",
        "-t", f"{total_dur:.2f}",
        str(output_file)
    ])
    subprocess.run(mux_cmd, check=True)

    if qc_file:
        generate_contact_sheet(output_file, qc_file, num_frames=12, aspect="16:9")

    shutil.rmtree(tmp_dir, ignore_errors=True)
    qc_res = validate_deliverable(output_file, expected_aspect="16:9")
    return {
        "output_file": str(output_file),
        "qc_file": str(qc_file) if qc_file else None,
        "qc_validation": qc_res
    }
