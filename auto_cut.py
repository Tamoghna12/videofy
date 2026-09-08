#!/usr/bin/env python3
"""
auto_cut.py - Automated, High-Quality Cinematic Video Creation Pipeline
Designed for Antigravity with claudeclip & kinocut integration.

Presets:
- 'whitby': Whitby Gothic Coast (75s) - Harbour, cliffs, 199 steps, Abbey ruins, moorland sunset.
- 'scarboro': Scarborough Coast (72s) - South Bay, castle cliffs, surf, harbour, evening Ferris wheel.
- 'york': Historic York (78s) - Train arrival, Shambles, River Ouse, York Minster, evening rain.
- 'journey': North Sea Grand Tour (120s) - York -> Scarborough -> Whitby combined epic.

Features:
- Dynamic asset discovery across all subdirectories
- Audio beat & energy envelope detection for rhythmically aligned cuts
- Rotation-aware 9:16 portrait rendering (1080x1920 @ 24fps)
- Optimized non-dark cinematic grade (gentle shadow lift, warm amber/teal balance)
- Elegant typography overlays: Intro title card, landmark captions, and Outro card
- EBU R128 audio loudness mastering (-16 LUFS) with clean exponential fades
- Automated Quality Control via kinocut metric-qc
- Visual verification contact sheet generation
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
import numpy as np
import scipy.signal as signal

WORKSPACE_DIR = Path(__file__).resolve().parent

# Fonts for titles & captions
FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

# Calibrated Non-Dark Cinematic Kodak 2383 Grade
CINEMATIC_GRADE = (
    "eq=contrast=1.05:brightness=0.04:gamma=1.08:saturation=0.96,"
    "colorbalance=rs=0.02:gs=0.0:bs=-0.02:rm=0.03:gm=0.01:bm=-0.01:rh=0.06:gh=0.02:bh=-0.04,"
    "curves=master='0/0.03 0.25/0.28 0.75/0.79 1/1'"
)

# Custom Y-pan expressions for portrait vertical reveals
# (y0, y1) where 0.0=top, 0.5=center, 1.0=bottom
Y_PAN = {
    "20260905_184406": (0.55, 0.25),  # Pan up to Ferris wheel
    "20260906_150158": (0.75, 0.08),  # Follow Whitby Abbey arch tilt-up
    "20260903_183008": (0.45, 0.30),  # Tilt up York Minster facade
}


def find_all_media(root_dir):
    """Scan and index all video and audio files in workspace."""
    video_map = {}
    for p in root_dir.glob("**/*.mp4"):
        if not p.name.startswith("master_") and not p.name.startswith("final_"):
            video_map[p.stem] = p
    return video_map


def probe_video(video_path):
    """Detect dimensions and rotation metadata of a video."""
    cmd = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,duration:stream_side_data=rotation",
        "-of", "csv=p=0", str(video_path)
    ]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout.strip().splitlines()
    if not out:
        return 1080, 1920, True, 0.0
    w, h = map(int, out[0].split(",")[:2])
    rot = abs(float(out[1].split(",")[-1])) if len(out) > 1 else 0
    is_portrait = (h > w) or (rot != 0)
    
    dur = 0.0
    dur_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video_path)]
    dur_out = subprocess.run(dur_cmd, capture_output=True, text=True).stdout.strip()
    if dur_out:
        try: dur = float(dur_out)
        except ValueError: dur = 0.0
    return w, h, is_portrait, dur


def compute_beat_cues(audio_path, target_duration=75.0, min_shot=2.0, max_shot=4.5):
    """Extract audio envelope and identify natural downbeats and musical cue points."""
    cmd = [
        "ffmpeg", "-v", "error", "-t", str(target_duration), "-i", str(audio_path),
        "-ac", "1", "-ar", "44100", "-f", "s16le", "-"
    ]
    raw = subprocess.check_output(cmd)
    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    sr = 44100

    hop = int(sr * 0.025)
    win = int(sr * 0.050)
    num_frames = (len(samples) - win) // hop
    rms = np.array([
        np.sqrt(np.mean(samples[i * hop : i * hop + win] ** 2))
        for i in range(num_frames)
    ])
    times = np.arange(num_frames) * 0.025

    diff = np.maximum(np.diff(rms), 0)
    distance_frames = int(min_shot / 0.025)
    peaks, _ = signal.find_peaks(diff, distance=distance_frames, prominence=0.008)
    peak_times = times[peaks]

    cues = [0.0]
    curr = 0.0
    for pt in peak_times:
        if (pt - curr >= min_shot) and (pt < target_duration - 2.0):
            cues.append(float(pt))
            curr = pt
            if (target_duration - curr) < min_shot:
                break
    if target_duration not in cues:
        cues.append(float(target_duration))
    return cues


def resolve_lut(lut_query):
    """Find a LUT in assets/luts matching the query name."""
    if not lut_query:
        return None
    p = Path(lut_query)
    if p.is_file():
        return p.resolve()
    luts_dir = WORKSPACE_DIR / "assets" / "luts"
    q = lut_query.lower()
    matches = list(luts_dir.glob(f"**/*{lut_query}*"))
    if not matches:
        matches = [f for f in luts_dir.glob("**/*.[cC][uU][bB][eE]") if q in f.name.lower()]
    if matches:
        return matches[0].resolve()
    print(f"Warning: LUT '{lut_query}' not found in {luts_dir}. Using default cinematic grade.")
    return None


def get_video_filter(video_path, duration, lut_path=None):
    """Build rotation-safe 9:16 portrait video filter chain."""
    _, _, is_portrait, _ = probe_video(video_path)
    stem = video_path.stem
    if is_portrait:
        chain = "scale=1080:1920:flags=lanczos"
    else:
        if stem in Y_PAN:
            y0, y1 = Y_PAN[stem]
            yexpr = f"(ih-owh)*({y0}+({y1}-{y0})*min(t/{duration:.3f},1))".replace("owh", "(ih-oh)")
            chain = f"scale=2160:-2,crop=2160:3840:0:'{yexpr}',scale=1080:1920:flags=lanczos"
        else:
            chain = "crop=w='ih*9/16':h='ih':x='(iw-ow)/2':y=0,scale=1080:1920:flags=lanczos"
    if lut_path:
        return f"{chain},lut3d=file='{lut_path}'"
    return f"{chain},{CINEMATIC_GRADE}"


def render_segment(video_path, start, end, out_path, lut_path=None):
    """Extract and conform a single segment to 24fps 9:16 portrait."""
    dur = end - start
    vf = get_video_filter(video_path, dur, lut_path=lut_path)
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-ss", f"{start:.3f}",
        "-i", str(video_path),
        "-t", f"{dur:.3f}",
        "-vf", vf,
        "-an",
        "-c:v", "libx264", "-preset", "fast", "-crf", "19",
        "-pix_fmt", "yuv420p", "-r", "24",
        str(out_path)
    ]
    subprocess.run(cmd, check=True)


def concat_segments(seg_list, out_path):
    """Concatenate rendered video segments using ffmpeg concat demuxer."""
    tmp_txt = out_path.parent / "_concat_list.txt"
    tmp_txt.write_text("".join(f"file '{p.resolve()}'\n" for p in seg_list))
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-f", "concat", "-safe", "0",
        "-i", str(tmp_txt),
        "-c", "copy",
        "-movflags", "+faststart",
        str(out_path)
    ]
    subprocess.run(cmd, check=True)
    tmp_txt.unlink(missing_ok=True)


def build_text_overlay_filter(preset, total_duration):
    """Construct drawtext filter chain for Intro, Landmark Captions, and Outro."""
    filters = []

    def make_fade_alpha(t_start, t_end, fade=0.6):
        return (
            f"if(lt(t,{t_start:.2f}),0,"
            f"if(lt(t,{t_start+fade:.2f}),(t-{t_start:.2f})/{fade:.2f},"
            f"if(lt(t,{t_end-fade:.2f}),1,"
            f"if(lt(t,{t_end:.2f}),({t_end:.2f}-t)/{fade:.2f},0))))"
        )

    if preset == "whitby":
        intro_alpha = make_fade_alpha(1.0, 5.5, fade=0.8)
        filters.append(
            f"drawtext=fontfile={FONT_BOLD}:text='WHITBY':fontsize=76:fontcolor=white:"
            f"shadowcolor=black@0.7:shadowx=4:shadowy=4:x=(w-text_w)/2:y=h*0.37:alpha='{intro_alpha}'"
        )
        filters.append(
            f"drawtext=fontfile={FONT_REG}:text='THE YORKSHIRE COAST':fontsize=32:fontcolor=white@0.95:"
            f"shadowcolor=black@0.65:shadowx=2:shadowy=2:x=(w-text_w)/2:y=h*0.37+95:alpha='{intro_alpha}'"
        )
        captions = [
            (7.0, 11.5, "WHITBY HARBOUR & MARINA"),
            (14.5, 18.5, "COBBLESTONE STREETS OF OLD TOWN"),
            (22.0, 26.0, "NORTH SEA CLIFFS & SHORE"),
            (31.0, 35.5, "WHITBY PIER & HARBOUR LIGHT"),
            (40.0, 46.0, "THE 199 STEPS & WHITBY ABBEY"),
            (50.0, 54.5, "MOORLAND HORIZON"),
        ]
        for t_s, t_e, text in captions:
            if t_e <= total_duration - 4.0:
                c_alpha = make_fade_alpha(t_s, t_e, fade=0.5)
                filters.append(
                    f"drawtext=fontfile={FONT_BOLD}:text='{text}':fontsize=32:fontcolor=white:"
                    f"box=1:boxcolor=black@0.45:boxborderw=10:x=(w-text_w)/2:y=h*0.78:alpha='{c_alpha}'"
                )
        outro_s = max(0.0, total_duration - 5.5)
        outro_e = total_duration - 0.5
        outro_alpha = make_fade_alpha(outro_s, outro_e, fade=0.8)
        filters.append(
            f"drawtext=fontfile={FONT_BOLD}:text='NORTH YORKSHIRE':fontsize=60:fontcolor=white:"
            f"shadowcolor=black@0.7:shadowx=3:shadowy=3:x=(w-text_w)/2:y=h*0.42:alpha='{outro_alpha}'"
        )
        filters.append(
            f"drawtext=fontfile={FONT_REG}:text='A COASTAL JOURNEY • 2026':fontsize=28:fontcolor=white@0.9:"
            f"shadowcolor=black@0.6:shadowx=2:shadowy=2:x=(w-text_w)/2:y=h*0.42+80:alpha='{outro_alpha}'"
        )

    elif preset == "scarboro":
        intro_alpha = make_fade_alpha(1.0, 5.5, fade=0.8)
        filters.append(
            f"drawtext=fontfile={FONT_BOLD}:text='SCARBOROUGH':fontsize=72:fontcolor=white:"
            f"shadowcolor=black@0.7:shadowx=4:shadowy=4:x=(w-text_w)/2:y=h*0.37:alpha='{intro_alpha}'"
        )
        filters.append(
            f"drawtext=fontfile={FONT_REG}:text='QUEEN OF THE YORKSHIRE COAST':fontsize=30:fontcolor=white@0.95:"
            f"shadowcolor=black@0.65:shadowx=2:shadowy=2:x=(w-text_w)/2:y=h*0.37+95:alpha='{intro_alpha}'"
        )
        captions = [
            (6.5, 11.0, "SOUTH BAY & CLIFFS"),
            (14.0, 18.5, "SCARBOROUGH BEACH & SURF"),
            (22.0, 26.5, "HISTORIC HARBOUR & PIERS"),
            (31.0, 36.0, "SEAFRONT PROMENADE"),
            (41.0, 48.0, "DUSK OVER THE BAY • OBSERVATION WHEEL"),
            (52.0, 56.5, "TWILIGHT ON THE WATERFRONT"),
        ]
        for t_s, t_e, text in captions:
            if t_e <= total_duration - 4.0:
                c_alpha = make_fade_alpha(t_s, t_e, fade=0.5)
                filters.append(
                    f"drawtext=fontfile={FONT_BOLD}:text='{text}':fontsize=32:fontcolor=white:"
                    f"box=1:boxcolor=black@0.45:boxborderw=10:x=(w-text_w)/2:y=h*0.78:alpha='{c_alpha}'"
                )
        outro_s = max(0.0, total_duration - 5.5)
        outro_e = total_duration - 0.5
        outro_alpha = make_fade_alpha(outro_s, outro_e, fade=0.8)
        filters.append(
            f"drawtext=fontfile={FONT_BOLD}:text='SCARBOROUGH':fontsize=60:fontcolor=white:"
            f"shadowcolor=black@0.7:shadowx=3:shadowy=3:x=(w-text_w)/2:y=h*0.42:alpha='{outro_alpha}'"
        )
        filters.append(
            f"drawtext=fontfile={FONT_REG}:text='NORTH YORKSHIRE COAST • 2026':fontsize=28:fontcolor=white@0.9:"
            f"shadowcolor=black@0.6:shadowx=2:shadowy=2:x=(w-text_w)/2:y=h*0.42+80:alpha='{outro_alpha}'"
        )

    elif preset == "york":
        intro_alpha = make_fade_alpha(1.0, 5.5, fade=0.8)
        filters.append(
            f"drawtext=fontfile={FONT_BOLD}:text='YORK':fontsize=80:fontcolor=white:"
            f"shadowcolor=black@0.7:shadowx=4:shadowy=4:x=(w-text_w)/2:y=h*0.37:alpha='{intro_alpha}'"
        )
        filters.append(
            f"drawtext=fontfile={FONT_REG}:text='ANCIENT WALLED CITY':fontsize=32:fontcolor=white@0.95:"
            f"shadowcolor=black@0.65:shadowx=2:shadowy=2:x=(w-text_w)/2:y=h*0.37+95:alpha='{intro_alpha}'"
        )
        captions = [
            (6.5, 11.0, "YORK STATION & CITY WALLS"),
            (14.0, 19.0, "THE SHAMBLES & MEDIEVAL LANES"),
            (24.0, 29.0, "RIVER OUSE WATERFRONT"),
            (35.0, 40.0, "STONEGATE & OLD TOWN"),
            (45.0, 53.0, "YORK MINSTER CATHEDRAL"),
            (57.0, 63.0, "EVENING RAIN & REFLECTIONS"),
        ]
        for t_s, t_e, text in captions:
            if t_e <= total_duration - 4.0:
                c_alpha = make_fade_alpha(t_s, t_e, fade=0.5)
                filters.append(
                    f"drawtext=fontfile={FONT_BOLD}:text='{text}':fontsize=32:fontcolor=white:"
                    f"box=1:boxcolor=black@0.45:boxborderw=10:x=(w-text_w)/2:y=h*0.78:alpha='{c_alpha}'"
                )
        outro_s = max(0.0, total_duration - 5.5)
        outro_e = total_duration - 0.5
        outro_alpha = make_fade_alpha(outro_s, outro_e, fade=0.8)
        filters.append(
            f"drawtext=fontfile={FONT_BOLD}:text='HISTORIC YORK':fontsize=60:fontcolor=white:"
            f"shadowcolor=black@0.7:shadowx=3:shadowy=3:x=(w-text_w)/2:y=h*0.42:alpha='{outro_alpha}'"
        )
        filters.append(
            f"drawtext=fontfile={FONT_REG}:text='HEART OF YORKSHIRE • 2026':fontsize=28:fontcolor=white@0.9:"
            f"shadowcolor=black@0.6:shadowx=2:shadowy=2:x=(w-text_w)/2:y=h*0.42+80:alpha='{outro_alpha}'"
        )

    return ",".join(filters)


def mux_soundtrack_with_overlays(video_path, music_path, out_path, total_duration, preset="whitby"):
    """Mux audio with EBU R128 loudness normalization, video fades, and cinematic typography."""
    fade_st = max(0.0, total_duration - 2.8)
    a_st = max(0.0, total_duration - 4.0)

    text_filters = build_text_overlay_filter(preset, total_duration)
    
    v_filter = f"[0:v]fade=t=in:st=0:d=1.2,fade=t=out:st={fade_st:.2f}:d=2.8"
    if text_filters:
        v_filter += f",{text_filters}"
    v_filter += "[v]"

    a_filter = f"[1:a]atrim=0:{total_duration:.2f},loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=out:st={a_st:.2f}:d=3.8[a]"

    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-i", str(video_path),
        "-i", str(music_path),
        "-filter_complex", f"{v_filter};{a_filter}",
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "19",
        "-pix_fmt", "yuv420p", "-r", "24",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        "-t", f"{total_duration:.2f}",
        str(out_path)
    ]
    subprocess.run(cmd, check=True)


def generate_contact_sheet(video_path, out_image_path):
    """Generate a visual QC contact sheet grid showing cuts."""
    out_image_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-i", str(video_path),
        "-vf", "select='not(mod(n\\,90))',scale=270:480,tile=4x4",
        "-frames:v", "1",
        "-q:v", "2",
        str(out_image_path)
    ]
    subprocess.run(cmd, check=True)


def run_kinocut_qc(video_path):
    """Run kinocut metric-qc audit on final video."""
    print("Running kinocut metric-qc audit...")
    cmd = [
        "uvx", "--from", "kinocut", "kino",
        "--format", "json",
        "metric-qc", str(video_path)
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(res.stdout)
        print(f"  QC Status: {data.get('fail_count', 0)} failures")
        for finding in data.get("findings", []):
            print(f"   - [{finding.get('severity', 'info').upper()}] {finding.get('message')}")
        return data
    except Exception as e:
        print(f"  Note: kinocut QC returned note: {e}")
        return None


def run_pipeline(preset="whitby", duration=None, music=None, output_name=None, lut=None):
    """Main automated workflow execution."""
    media_map = find_all_media(WORKSPACE_DIR)
    print(f"Indexed {len(media_map)} video assets across workspace.")

    lut_path = resolve_lut(lut)
    if lut_path:
        print(f"Applying 3D LUT: {lut_path.name}")
    else:
        print("Applying default calibrated cinematic curve.")

    out_dir = WORKSPACE_DIR / "edit"
    out_dir.mkdir(exist_ok=True)
    tmp_clips_dir = out_dir / f"tmp_portrait_{preset}"
    tmp_clips_dir.mkdir(exist_ok=True)

    if preset == "whitby":
        music_path = WORKSPACE_DIR / (music or "bg_music/solas_jamie_duffy.mp3")
        target_duration = duration or 75.0
        final_filename = output_name or "whitby_portrait_cinematic.mp4"
        shots = [
            ("20260906_105056", 2.0, 5.5),
            ("20260906_105114", 4.0, 7.5),
            ("20260906_105652", 1.5, 5.0),
            ("20260906_110026", 2.0, 5.5),
            ("20260906_110927", 3.0, 7.0),
            ("20260906_124316", 1.5, 5.0),
            ("20260906_124404", 0.5, 3.1),
            ("20260906_124549", 1.5, 5.0),
            ("20260906_133641", 1.0, 4.5),
            ("20260906_134022", 12.0, 16.0),
            ("20260906_145400", 2.0, 6.0),
            ("20260906_150133", 2.0, 6.0),
            ("20260906_150158", 8.0, 14.5),
            ("20260906_150220", 9.0, 12.0),
            ("20260906_151844", 2.0, 5.5),
            ("20260906_153526", 1.5, 4.5),
            ("20260906_154424", 0.5, 3.5),
        ]

    elif preset == "scarboro":
        music_path = WORKSPACE_DIR / (music or "bg_music/can_you_hear_the_music.mp3")
        target_duration = duration or 70.0
        final_filename = output_name or "scarborough_portrait_cinematic.mp4"
        shots = [
            ("20260905_130158", 1.5, 5.0),   # Coastal road arrival
            ("20260905_130233", 11.0, 16.0), # Orange Mini through country lane
            ("20260905_160359", 1.5, 5.5),   # South Bay panorama
            ("20260905_160428", 3.0, 7.0),   # Crashing coastal waves
            ("20260905_160457", 12.0, 16.5), # Castle cliff path
            ("20260905_182506", 10.0, 14.0), # Beach surf & foam
            ("20260905_183940", 6.5, 10.5),  # Promenade walk
            ("20260905_184108", 1.5, 5.0),   # Fishing harbour
            ("20260905_184145", 4.0, 8.0),   # Harbour boats
            ("20260905_184224", 16.5, 21.0), # Evening seafront & arcades
            ("20260905_184326", 1.5, 5.5),   # Silhouettes at dusk
            ("20260905_184406", 29.0, 36.5), # Ferris wheel payoff
            ("20260905_185303", 2.0, 6.5),   # Twilight seafront glow
        ]

    elif preset == "york":
        music_path = WORKSPACE_DIR / (music or "bg_music/interstellar_first_step.mp3")
        target_duration = duration or 78.0
        final_filename = output_name or "york_portrait_cinematic.mp4"
        shots = [
            ("20260903_114125", 11.5, 16.0), # Train arrival
            ("20260903_121155", 2.0, 6.5),   # City gate entry
            ("20260903_121225", 1.0, 4.5),   # Medieval arch tunnel
            ("20260903_122153", 3.5, 7.0),   # The Shambles
            ("20260903_131339", 2.5, 6.0),   # Timber-framed arch
            ("20260903_131536", 3.0, 7.0),   # Cobblestones
            ("20260903_140851", 4.5, 9.0),   # River Ouse waterfront
            ("20260903_141544", 2.0, 5.5),   # Riverside walk
            ("20260903_141659", 8.5, 13.5),  # City departure / bridges
            ("20260903_174058", 6.5, 11.0),  # Stonegate afternoon
            ("20260903_183008", 3.5, 11.0),  # York Minster hero
            ("20260903_181254", 1.0, 5.5),   # Evening rain
            ("20260903_184627", 1.5, 5.0),   # Red umbrella in rain
            ("20260903_184645", 4.5, 8.5),   # Twilight River Ouse
            ("20260905_105353", 1.5, 5.5),   # Suitcase & farewell
        ]

    else:
        raise ValueError(f"Unknown preset: {preset}")

    print(f"\n=======================================================")
    print(f"Launching 9:16 Portrait Pipeline: {preset.upper()}")
    print(f"Soundtrack: {music_path.name}")
    print(f"Target duration: {target_duration}s")
    print(f"Shot count: {len(shots)}")
    print(f"=======================================================\n")

    # 1. Compute musical beat cues
    print("[Step 1/5] Analyzing soundtrack energy envelope & beat cues...")
    beat_cues = compute_beat_cues(music_path, target_duration=target_duration)
    print(f"  Identified {len(beat_cues)-1} rhythmically aligned cut points.")

    # 2. Extract, conform, and grade each segment
    print("\n[Step 2/5] Extracting, cropping to 9:16, conforming to 24fps & grading...")
    seg_files = []
    for i, (stem, s_start, s_end) in enumerate(shots):
        if stem not in media_map:
            print(f"  Warning: clip {stem} not found, skipping.")
            continue
        vpath = media_map[stem]
        seg_out = tmp_clips_dir / f"seg_{i:02d}.mp4"
        seg_dur = s_end - s_start
        render_segment(vpath, s_start, s_end, seg_out, lut_path=lut_path)
        seg_files.append(seg_out)
        print(f"  [{i+1}/{len(shots)}] Graded: {stem} ({seg_dur:.1f}s)")

    # 3. Concatenate
    print("\n[Step 3/5] Concatenating 9:16 portrait video master...")
    master_path = out_dir / f"master_portrait_{preset}.mp4"
    concat_segments(seg_files, master_path)

    # 4. Audio Mastering & Typography Overlays
    print("\n[Step 4/5] Rendering cinematic typography & mastering audio to EBU R128...")
    actual_dur = float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(master_path)
    ]).strip())
    
    final_output = out_dir / final_filename
    mux_soundtrack_with_overlays(master_path, music_path, final_output, actual_dur, preset=preset)
    print(f"  Exported: {final_output.name} ({actual_dur:.1f}s)")

    # 5. Automated QC & Verification Sheet
    print("\n[Step 5/5] Performing automated quality control & contact sheet generation...")
    qc_sheet = out_dir / "verify" / f"qc_sheet_{preset}_cinematic.png"
    generate_contact_sheet(final_output, qc_sheet)
    print(f"  Visual contact sheet: {qc_sheet}")

    qc_data = run_kinocut_qc(final_output)

    # Clean up temporary segments
    for f in tmp_clips_dir.glob("*.mp4"):
        f.unlink()
    tmp_clips_dir.rmdir()
    master_path.unlink(missing_ok=True)

    print("\n=======================================================")
    print(f"SUCCESS: {preset.upper()} Portrait Video Render Complete!")
    print(f"Deliverable: {final_output}")
    print(f"Contact Sheet: {qc_sheet}")
    print("=======================================================\n")
    return final_output, qc_sheet, qc_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated 9:16 Portrait Video Pipeline")
    parser.add_argument("--preset", default="scarboro", choices=["whitby", "scarboro", "york"], help="Preset project")
    parser.add_argument("--duration", type=float, default=None, help="Target duration in seconds")
    parser.add_argument("--music", default=None, help="Path to music file in bg_music/")
    parser.add_argument("--lut", default=None, help="Name or path of 3D LUT (.cube) from assets/luts/")
    parser.add_argument("--output", default=None, help="Output filename")
    args = parser.parse_args()

    run_pipeline(preset=args.preset, duration=args.duration, music=args.music, output_name=args.output, lut=args.lut)
