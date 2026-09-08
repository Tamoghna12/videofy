#!/usr/bin/env python3
"""
Bradford Reels Generator:
Creates 3 high-impact 9:16 Instagram Reels from raw footage in raw_footage/bradford/:
  Reel 1: "Arriving in Bradford | The Journey" (Travel Vlog)
  Reel 2: "Solo Dining & Evening Reset" (Lifestyle / Food Vlog)
  Reel 3: "Bradford City Hall & Twilight Glow" (Cinematic Architecture)
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

WORKSPACE_DIR = Path("/home/tamoghna/Documents/Video_editing")
BRADFORD_DIR = WORKSPACE_DIR / "raw_footage" / "bradford"
EDIT_DIR = WORKSPACE_DIR / "edit"
VERIFY_DIR = EDIT_DIR / "verify"
ASSETS_DIR = WORKSPACE_DIR / "assets"
MUSIC_DIR = WORKSPACE_DIR / "bg_music"

FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

EDIT_DIR.mkdir(exist_ok=True)
VERIFY_DIR.mkdir(exist_ok=True)


REELS_CONFIG = {
    "reel1": {
        "title": "Arriving in Bradford",
        "output_name": "bradford_reel1_the_journey.mp4",
        "music": "experience_einaudi.mp3",
        "music_start": 0.0,
        "lut": "CINECOLOR_GOLDEN_HOUR.CUBE",
        "intro_main": "BRADFORD, UK",
        "intro_sub": "THE JOURNEY BEGINS",
        "outro_main": "YORKSHIRE TRAVELS",
        "outro_sub": "Follow for Part 2",
        "shots": [
            ("DJI_20260531141209_0261_D.MP4", 3.0, 7.0, "Travelling through Yorkshire countryside"),
            ("DJI_20260723171555_0262_D.MP4", 1.5, 5.0, "Arriving at Bradford Interchange"),
            ("DJI_20260723171615_0263_D.MP4", 2.0, 5.5, "Stepping onto the platform"),
            ("DJI_20260723171641_0264_D.MP4", 1.0, 4.5, "Bradford city center welcome"),
            ("DJI_20260723171744_0265_D.MP4", 2.0, 6.0, "Stepping into the historic city"),
            ("DJI_20260723171945_0266_D.MP4", 2.0, 6.5, "Victorian Railway Arches • Built 1850"),
            ("DJI_20260723173540_0270_D.MP4", 4.0, 8.5, "Exploring historic Little Germany"),
            ("DJI_20260723174010_0271_D.MP4", 2.0, 6.0, "Timeless Yorkshire stone architecture"),
            ("DJI_20260723180816_0273_D.MP4", 1.0, 4.5, "Checking into our room"),
            ("DJI_20260723183212_0274_D.MP4", 1.0, 4.5, "Journey complete • Relaxing evening ahead"),
        ]
    },
    "reel2": {
        "title": "Solo Dining & Evening Reset",
        "output_name": "bradford_reel2_solo_dining.mp4",
        "music": "debussy_clair_de_lune.mp3",
        "music_start": 4.0,
        "lut": None,  # Custom appetizing warm grade
        "intro_main": "SOLO TRAVEL EVENINGS",
        "intro_sub": "Dinner by the Window • Bradford",
        "outro_main": "SLOW TRAVEL JOURNAL",
        "outro_sub": "Savoring every moment",
        "shots": [
            ("DJI_20260723195704_0275_D.MP4", 1.5, 5.5, "Golden afternoon light by the window"),
            ("DJI_20260723200841_0277_D.MP4", 2.0, 5.5, "Taking time to pause and slow down"),
            ("DJI_20260723202023_0278_D.MP4", 508.0, 513.0, "Fresh salad & grilled dinner is served"),
            ("DJI_20260723202023_0278_D.MP4", 630.0, 634.5, "The best feeling after a day of travel"),
            ("DJI_20260723202023_0278_D.MP4", 750.0, 755.0, "Quiet comfort & delicious food"),
            ("DJI_20260723202023_0278_D.MP4", 1110.0, 1114.5, "A cold refreshing drink to finish"),
            ("DJI_20260723202023_0278_D.MP4", 1228.0, 1233.0, "Watching dusk settle over the city"),
            ("DJI_20260723214931_0284_D.MP4", 1.5, 5.5, "Goodnight Bradford"),
        ]
    },
    "reel3": {
        "title": "Bradford City Hall & Twilight Glow",
        "output_name": "bradford_reel3_city_hall_twilight.mp4",
        "music": "can_you_hear_the_music.mp3",
        "music_start": 0.0,
        "lut": "Rec709 Kodak 2383 D65.cube",
        "intro_main": "BRADFORD CITY HALL",
        "intro_sub": "A Victorian Gothic Masterpiece",
        "outro_main": "DISCOVER YORKSHIRE",
        "outro_sub": "Bradford • City of Culture",
        "shots": [
            ("DJI_20260723174010_0271_D.MP4", 3.0, 7.0, "Historic Victorian bank architecture"),
            ("DJI_20260723204601_0280_D.MP4", 12.0, 16.5, "Approaching Centenary Square at dusk"),
            ("DJI_20260723205102_0281_D.MP4", 5.0, 9.5, "Strolling through City Park promenade"),
            ("DJI_20260723205159_0282_D.MP4", 4.0, 8.5, "The grand civic heart of Bradford"),
            ("DJI_20260723205446_0283_D.MP4", 0.5, 6.0, "The Iconic 220-ft Clock Tower"),
            ("DJI_20260723205446_0283_D.MP4", 18.0, 23.0, "Venetian Gothic Elegance • Built 1873"),
            ("DJI_20260723205446_0283_D.MP4", 30.0, 34.5, "Grade I Listed Heritage in golden light"),
            ("DJI_20260723204601_0280_D.MP4", 28.0, 32.5, "Twilight magic falling over Yorkshire"),
        ]
    }
}


def find_lut_file(lut_name):
    if not lut_name:
        return None
    p = ASSETS_DIR / "luts"
    matches = list(p.glob(f"**/*{lut_name}*"))
    if matches:
        return matches[0].resolve()
    return None


def render_shot_segment(src_path, start, end, out_path, lut_file=None, is_warm_food_grade=False):
    """Render a trimmed segment conformed to 1920x1080 (16:9 Landscape) @ 24fps."""
    dur = end - start
    
    # 16:9 Landscape conform with subtle Ken Burns push-in
    zoom_expr = f"scale=eval=frame:w='1920*(1+0.02*t/{dur:.3f})':h='1080*(1+0.02*t/{dur:.3f})'"
    base_chain = (
        f"scale=1920:1080:force_original_aspect_ratio=increase,"
        f"crop=1920:1080:(iw-ow)/2:(ih-oh)/2,"
        f"{zoom_expr},"
        f"crop=1920:1080:(iw-ow)/2:(ih-oh)/2"
    )

    if lut_file and Path(lut_file).exists():
        color_filter = f"lut3d=file='{lut_file}'"
    elif is_warm_food_grade:
        color_filter = (
            "eq=contrast=1.06:brightness=0.03:saturation=1.08:gamma=1.06,"
            "curves=master='0/0.02 0.5/0.52 1/1'"
        )
    else:
        color_filter = (
            "eq=contrast=1.05:brightness=0.04:gamma=1.08:saturation=0.98,"
            "curves=master='0/0.03 0.25/0.28 0.75/0.79 1/1'"
        )

    vf = f"{base_chain},{color_filter}"

    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-ss", f"{start:.3f}",
        "-i", str(src_path),
        "-t", f"{dur:.3f}",
        "-vf", vf,
        "-r", "24",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "19",
        "-pix_fmt", "yuv420p",
        "-an",
        str(out_path)
    ]
    subprocess.run(cmd, check=True)


def build_reel_overlays(total_duration, intro_main, intro_sub, outro_main, outro_sub, shot_captions):
    """Create FFmpeg drawtext and progress bar filter graph for 16:9 Landscape."""
    filters = []

    # 1. Top animated progress bar (gold accent)
    filters.append(
        f"drawbox=x=0:y=0:w='1920*(t/{total_duration:.3f})':h=6:color=0xE5A93C@1:t=fill"
    )

    # 2. Intro Title Card (0.4s - 3.6s with smooth fade in lower-left)
    intro_start = 0.4
    intro_end = 3.6
    intro_alpha = f"if(between(t,{intro_start},{intro_end}),if(lt(t,{intro_start+0.4}),(t-{intro_start})/0.4,if(gt(t,{intro_end-0.4}),({intro_end}-t)/0.4,1)),0)"

    filters.append(
        f"drawbox=x=100:y=720:w=720:h=150:color=black@0.65:t=fill:enable='between(t,{intro_start},{intro_end})'"
    )
    filters.append(
        f"drawbox=x=95:y=720:w=5:h=150:color=0xE5A93C@0.95:t=fill:enable='between(t,{intro_start},{intro_end})'"
    )
    filters.append(
        f"drawtext=fontfile='{FONT_BOLD}':text='{intro_main}':fontsize=48:fontcolor=white:x=125:y=745:alpha='{intro_alpha}'"
    )
    filters.append(
        f"drawtext=fontfile='{FONT_REG}':text='{intro_sub}':fontsize=24:fontcolor=0xE0E0E0:x=127:y=808:alpha='{intro_alpha}'"
    )

    # 3. Shot Captions (Centered lower-third)
    curr_time = 0.0
    for dur, caption in shot_captions:
        cap_start = curr_time + 0.3
        cap_end = curr_time + dur - 0.3
        if cap_end > cap_start + 0.5:
            cap_alpha = f"if(between(t,{cap_start:.2f},{cap_end:.2f}),if(lt(t,{cap_start+0.3:.2f}),(t-{cap_start:.2f})/0.3,if(gt(t,{cap_end-0.3:.2f}),({cap_end:.2f}-t)/0.3,1)),0)"
            filters.append(
                f"drawbox=x=(w-1050)/2:y=950:w=1050:h=56:color=black@0.60:t=fill:enable='between(t,{cap_start:.2f},{cap_end:.2f})'"
            )
            filters.append(
                f"drawtext=fontfile='{FONT_BOLD}':text='{caption}':fontsize=26:fontcolor=white:x=(w-text_w)/2:y=965:alpha='{cap_alpha}'"
            )
        curr_time += dur

    # 4. Outro Card (Center modal card during last 3.5 seconds)
    outro_start = max(0.0, total_duration - 3.5)
    outro_alpha = f"if(between(t,{outro_start:.2f},{total_duration:.2f}),if(lt(t,{outro_start+0.4:.2f}),(t-{outro_start:.2f})/0.4,1),0)"

    filters.append(
        f"drawbox=x=(w-760)/2:y=(h-180)/2:w=760:h=180:color=black@0.75:t=fill:enable='between(t,{outro_start:.2f},{total_duration:.2f})'"
    )
    filters.append(
        f"drawbox=x=(w-760)/2:y=(h-180)/2:w=760:h=4:color=0xE5A93C@0.95:t=fill:enable='between(t,{outro_start:.2f},{total_duration:.2f})'"
    )
    filters.append(
        f"drawtext=fontfile='{FONT_BOLD}':text='{outro_main}':fontsize=46:fontcolor=white:x=(w-text_w)/2:y=485:alpha='{outro_alpha}'"
    )
    filters.append(
        f"drawtext=fontfile='{FONT_REG}':text='{outro_sub}':fontsize=26:fontcolor=0xE5A93C:x=(w-text_w)/2:y=555:alpha='{outro_alpha}'"
    )

    # 5. Creator watermark bug (Bottom left)
    filters.append(
        f"drawtext=fontfile='{FONT_REG}':text='@bradford.moments':fontsize=20:fontcolor=white@0.6:x=100:y=1030"
    )

    return ",".join(filters)


def generate_contact_sheet(video_path, output_png, num_frames=12):
    """Generate 12-frame contact sheet for QC inspection (16:9 Landscape frames)."""
    probe_cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video_path)
    ]
    dur = float(subprocess.check_output(probe_cmd).strip())
    timestamps = [dur * (i + 0.5) / num_frames for i in range(num_frames)]
    
    tmp_frames = []
    for i, ts in enumerate(timestamps):
        out_f = VERIFY_DIR / f"tmp_qc_{Path(video_path).stem}_{i:02d}.jpg"
        cmd = [
            "ffmpeg", "-y", "-ss", f"{ts:.3f}", "-i", str(video_path),
            "-vf", "scale=480:270", "-frames:v", "1", str(out_f)
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if out_f.exists():
            tmp_frames.append(out_f)

    if not tmp_frames:
        return

    cols = 4
    rows = (len(tmp_frames) + cols - 1) // cols
    w, h = 480, 270
    sheet = Image.new("RGB", (cols * w, rows * h), (15, 15, 15))
    draw = ImageDraw.Draw(sheet)

    for idx, frame_path in enumerate(tmp_frames):
        r = idx // cols
        c = idx % cols
        img = Image.open(frame_path)
        sheet.paste(img, (c * w, r * h))
        draw.rectangle([c * w, r * h + h - 28, c * w + w, r * h + h], fill=(0, 0, 0, 200))
        ts_val = timestamps[idx]
        draw.text((c * w + 12, r * h + h - 22), f"T = {ts_val:.1f}s", fill=(255, 255, 255))
        frame_path.unlink(missing_ok=True)

    sheet.save(output_png, quality=90)


def produce_reel(reel_key):
    cfg = REELS_CONFIG[reel_key]
    title = cfg["title"]
    out_file = EDIT_DIR / cfg["output_name"]
    lut_name = cfg["lut"]
    lut_path = find_lut_file(lut_name)
    music_file = MUSIC_DIR / cfg["music"]
    music_start = cfg["music_start"]
    is_food = (reel_key == "reel2")

    print(f"\n=======================================================")
    print(f"Producing: {title.upper()}")
    print(f"Output: {out_file.name}")
    print(f"LUT: {lut_path.name if lut_path else 'Warm Appetizing Grade'}")
    print(f"Music: {music_file.name} (from {music_start}s)")
    print(f"=======================================================")

    tmp_dir = EDIT_DIR / f"tmp_{reel_key}"
    tmp_dir.mkdir(exist_ok=True)

    # 1. Render all trimmed shots
    seg_paths = []
    shot_captions = []
    for idx, (filename, start, end, cap) in enumerate(cfg["shots"]):
        src_clip = BRADFORD_DIR / filename
        seg_file = tmp_dir / f"seg_{idx:02d}.mp4"
        dur = end - start
        shot_captions.append((dur, cap))
        print(f"  [{idx+1}/{len(cfg['shots'])}] Conforming {filename} ({dur:.1f}s)...")
        render_shot_segment(src_clip, start, end, seg_file, lut_file=lut_path, is_warm_food_grade=is_food)
        seg_paths.append(seg_file)

    # 2. Concat video track
    concat_list_file = tmp_dir / "concat_list.txt"
    with open(concat_list_file, "w") as f:
        for p in seg_paths:
            f.write(f"file '{p.resolve()}'\n")

    raw_concat_video = tmp_dir / "raw_concat.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list_file),
        "-c", "copy",
        str(raw_concat_video)
    ], check=True)

    # Measure total duration
    dur_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(raw_concat_video)]
    total_dur = float(subprocess.check_output(dur_cmd).strip())
    print(f"  Total timeline duration: {total_dur:.1f}s")

    # 3. Build overlays & mux audio
    print(f"  Applying typography, progress bar, & mastering soundtrack to EBU R128...")
    overlay_filters = build_reel_overlays(
        total_dur,
        cfg["intro_main"],
        cfg["intro_sub"],
        cfg["outro_main"],
        cfg["outro_sub"],
        shot_captions
    )

    # Audio chain: trim from music_start, apply fade-out over last 3s, normalize with loudnorm
    fade_out_start = max(0.0, total_dur - 3.0)
    audio_filter = f"afade=t=in:st=0:d=1.0,afade=t=out:st={fade_out_start:.2f}:d=3.0,loudnorm=I=-14:LRA=7:TP=-1.5"

    mux_cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-i", str(raw_concat_video),
        "-ss", f"{music_start:.2f}",
        "-i", str(music_file),
        "-vf", overlay_filters,
        "-af", audio_filter,
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "256k",
        "-shortest",
        str(out_file)
    ]
    subprocess.run(mux_cmd, check=True)
    print(f"  Exported deliverable: {out_file}")

    # 4. Generate QC contact sheet
    qc_sheet = VERIFY_DIR / f"qc_sheet_{reel_key}.png"
    print(f"  Generating QC contact sheet: {qc_sheet.name}...")
    generate_contact_sheet(out_file, qc_sheet)

    # Clean up tmp files
    shutil.rmtree(tmp_dir)

    print(f"SUCCESS: Finished {title} -> {out_file.name}\n")
    return out_file, qc_sheet


def main():
    target_reels = sys.argv[1:] if len(sys.argv) > 1 else ["reel1", "reel2", "reel3"]
    for rk in target_reels:
        if rk in REELS_CONFIG:
            produce_reel(rk)
        else:
            print(f"Unknown reel key: {rk}")

if __name__ == "__main__":
    main()
