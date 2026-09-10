"""
cinematic_landscape.py - Preset: 16:9 Widescreen Film Emulation
Applies Kodak 2383 D65 print film emulation, slow Ken Burns push-in,
cinematic title cards, top/bottom black letterboxing, cloned voiceover,
and kinetic highlighted ASS typography with GPU acceleration.
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
from ..core.beat_sync import detect_beats, snap_timeline_to_beats
from ..core.voiceover import generate_voiceover, generate_spaced_story_voiceover, is_voiceover_available
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
    beat_sync=False,
    smart_crop=False,
    voiceover_text=None,
    voiceover_speed=0.92,
    black_bars=False,
    shots=None,
    **kwargs
):
    footage_dir = Path(footage_dir)
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    tmp_dir = output_file.parent / f"_tmp_{output_file.stem}"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    color_vf = get_color_filter(grade_type=grade_preset, lut_name=lut_name)
    timeline_segments = []
    shot_captions = []
    shot_voiceovers = []
    shot_voiceover_starts = []
    curr_total = 0.0

    # Resolve audio & optional beat transients for musical synchronization
    music_file = resolve_audio(music_track) or resolve_audio("experience_einaudi.mp3")
    waves_file = resolve_audio(sfx_track, is_sfx=True) or resolve_audio("ocean_waves_crashing.mp3", is_sfx=True)

    detected_beats = []
    if beat_sync and music_file:
        print("🎵 Analyzing audio rhythm and downbeats for widescreen cinematic cuts...")
        beat_info = detect_beats(music_file, duration=max_duration)
        detected_beats = beat_info.get("beats", [])
        print(f"   Detected {len(detected_beats)} beat transients (Estimated {beat_info.get('tempo_estimate_bpm')} BPM)")

    if shots:
        # 1. Parse curated shot sequence
        parsed_shots = []
        for i, shot in enumerate(shots):
            if isinstance(shot, dict):
                fn = shot.get("file") or shot.get("filename") or shot.get("path")
                st = float(shot.get("start", 0.0))
                et = float(shot.get("end", st + 5.0))
                cap = shot.get("caption", f"Scene {i+1:02d}")
                vox = shot.get("voiceover") or shot.get("narration")
            elif len(shot) >= 4:
                fn, st, et, cap = shot[:4]
                vox = None
            else:
                fn, st, et = shot[:3]
                cap = f"Scene {i+1:02d}"
                vox = None
            
            src_path = footage_dir / fn if not Path(fn).is_absolute() else Path(fn)
            if not src_path.is_file():
                matches = list(footage_dir.glob(f"**/{src_path.name}"))
                if matches:
                    src_path = matches[0]
                else:
                    print(f"⚠️ Warning: shot file not found {fn}, skipping...")
                    continue
            
            parsed_shots.append({
                "src_path": src_path,
                "start": float(st),
                "end": float(et),
                "caption": cap,
                "raw_dur": float(et - st),
                "vox": vox,
                "voiceover_lead": float(shot.get("voiceover_lead", 0.5)) if isinstance(shot, dict) else 0.5
            })

        # Snap curated shot cuts to musical beats if enabled
        if beat_sync and detected_beats and parsed_shots:
            raw_durs = [s["raw_dur"] for s in parsed_shots]
            snapped_durs, _ = snap_timeline_to_beats(raw_durs, detected_beats)
            for s, s_dur in zip(parsed_shots, snapped_durs):
                s["end"] = s["start"] + s_dur
                s["dur"] = s_dur
        else:
            for s in parsed_shots:
                s["dur"] = s["raw_dur"]

        for i, s in enumerate(parsed_shots):
            dur = s["dur"]
            shot_start = curr_total
            if s.get("vox"):
                shot_voiceovers.append(s["vox"].strip())
                shot_voiceover_starts.append(shot_start + s.get("voiceover_lead", 0.5))

            seg_out = tmp_dir / f"seg_{i:02d}.mp4"
            if not (seg_out.is_file() and seg_out.stat().st_size > 100000):
                conform_clip(
                    s["src_path"],
                    start=s["start"],
                    end=s["end"],
                    out_path=seg_out,
                    target_res="1920x1080",
                    fps=24,
                    color_filter=color_vf,
                    zoom_rate=0.015,
                    accel=accel,
                    smart_crop=smart_crop
                )
            timeline_segments.append(seg_out)
            shot_captions.append((dur, s["caption"]))
            curr_total += dur
            if max_duration and curr_total >= max_duration:
                break
    else:
        vids = sorted(list(footage_dir.glob("*.mp4")) + list(footage_dir.glob("*.MP4")))
        if not vids:
            raise ValueError(f"No video files found in {footage_dir}")

        planned_vids = []
        raw_durations = []
        temp_total = 0.0
        v_idx = 0
        while temp_total < max_duration and v_idx < len(vids):
            v_path = vids[v_idx]
            dur = min(video_clip_duration, max_duration - temp_total)
            planned_vids.append(v_path)
            raw_durations.append(dur)
            temp_total += dur
            v_idx += 1

        if beat_sync and detected_beats:
            planned_durations, _ = snap_timeline_to_beats(raw_durations, detected_beats)
        else:
            planned_durations = raw_durations

        for seg_counter, (v_path, dur) in enumerate(zip(planned_vids, planned_durations)):
            seg_out = tmp_dir / f"seg_{seg_counter:02d}.mp4"
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
            if max_duration and curr_total >= max_duration:
                break

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

    # Voiceover & Kinetic Typography Synthesis
    vox_data = None
    # If shots defined per-shot voiceovers, prioritize them for exact visual synchronization
    if shot_voiceovers:
        voiceover_text = " | ".join(shot_voiceovers)
        sync_starts = shot_voiceover_starts
    else:
        sync_starts = None

    if voiceover_text and is_voiceover_available():
        vox_dir = tmp_dir / "voiceover"
        vox_speed = voiceover_speed if voiceover_speed != 1.15 else 0.92
        sub_margin_v = 45 if black_bars else 70
        sub_font_size = 32 if black_bars else 36
        try:
            vox_data = generate_spaced_story_voiceover(
                narration=voiceover_text,
                total_duration=total_dur,
                output_dir=vox_dir,
                speed=vox_speed,
                font_size=sub_font_size,
                margin_v=sub_margin_v,
                play_res_x=1920,
                play_res_y=1080,
                margin_lr=120,
                start_times=sync_starts
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

    # Overlays & Audio Mastering
    display_shot_captions = shot_captions if black_bars else ([] if (vox_data and vox_data.get("subtitles_ass")) else shot_captions)
    overlay_vf = build_timeline_overlays(
        total_dur,
        shot_captions=display_shot_captions,
        intro_title=title,
        intro_subtitle=subtitle,
        outro_title=outro_title,
        outro_subtitle=outro_subtitle,
        handle=handle,
        aspect="16:9",
        black_bars=black_bars
    )

    # Burn kinetic ASS highlighted subtitles
    if vox_data and vox_data.get("subtitles_ass"):
        ass_path = str(vox_data["subtitles_ass"]).replace("\\", "/").replace(":", "\\:")
        overlay_vf = f"{overlay_vf},ass='{ass_path}'"

    music_file = resolve_audio(music_track) or resolve_audio("experience_einaudi.mp3")
    waves_file = resolve_audio(sfx_track, is_sfx=True) or resolve_audio("ocean_waves_crashing.mp3", is_sfx=True)

    if vox_data and vox_data.get("ducking_intervals"):
        audio_vf = build_audio_filter(
            total_dur,
            music_volume=0.95,
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
            music_volume=0.95,
            sfx_volume=0.20,
            target_lufs=-16,
            has_sfx=True,
            voiceover_duration=vox_dur,
            voiceover_start=1.5
        )

    out_enc_args = get_encoder_args(preference=accel, crf=18, is_segment=False)
    mux_cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-i", str(raw_master),
        "-i", str(music_file),
        "-i", str(waves_file),
    ]
    if vox_data and vox_data.get("audio_file"):
        mux_cmd.extend(["-i", str(vox_data["audio_file"])])

    mux_cmd.extend([
        "-filter_complex", f"[0:v]{overlay_vf}[vout];{audio_vf}",
        "-map", "[vout]", "-map", "[aout]",
    ])
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

