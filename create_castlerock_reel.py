#!/usr/bin/env python3
"""
create_castlerock_reel.py
Generates a catchy 9:16 Instagram Reel for Castlerock, Northern Ireland.
Combines raw 1080p/4K video clips + batch-styled Polaroid snapshot cards
with camera shutter transitions, kinetic typography, top progress bar,
and viral Irish soundtrack (Jamie Duffy - Solas).
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageFilter

WORKSPACE_DIR = Path("/home/tamoghna/Documents/Video_editing")
CASTLEROCK_DIR = WORKSPACE_DIR / "raw_footage" / "Northern Ireland" / "castle_rock"
EDIT_DIR = WORKSPACE_DIR / "edit"
VERIFY_DIR = EDIT_DIR / "verify"
ASSETS_DIR = WORKSPACE_DIR / "assets"
MUSIC_DIR = WORKSPACE_DIR / "bg_music"
LUT_PATH = ASSETS_DIR / "luts" / "LUTs" / "CINECOLOR_GOLDEN_HOUR.CUBE"

FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

EDIT_DIR.mkdir(exist_ok=True)
VERIFY_DIR.mkdir(exist_ok=True)

# Curated Photos for Polaroid snapshots: (filename, title, subtitle, angle)
PHOTO_CARDS_DATA = [
    (
        "20240601_105138.jpg",
        "CASTLEROCK STATION",
        "Platform 1 • Causeway Coast Railway",
        -2.5
    ),
    (
        "20240601_110528.jpg",
        "COASTAL CAFE DELIGHTS",
        "Artisan Carrot Cake by the Sea",
        2.8
    ),
    (
        "20240601_115628.jpg",
        "DOWNHILL STRAND",
        "Wild Atlantic Waves & Golden Sands",
        -2.2
    ),
    (
        "20240601_120042_001.jpg",
        "VOLCANIC BASALT CLIFFS",
        "Exploring Ancient Causeway Coastlines",
        3.0
    ),
    (
        "20240601_140645.jpg",
        "THE OCEAN ROAD",
        "Winding Paths into the Atlantic",
        -1.8
    ),
]

# Curated Video Segments: (filename, start_sec, end_sec, caption)
VIDEO_SEGMENTS = [
    # Act I: Arrival & Village
    ("20240601_105607.mp4", 1.0, 4.2, "Arriving at picturesque Castlerock village"),
    ("20240601_105624.mp4", 1.5, 4.5, "First glimpse of the Atlantic horizon"),
    # Act II: Coastal walk & greenery
    ("20240601_123851.mp4", 3.0, 6.5, "Walking through the enchanted coastal glen"),
    ("20240601_143201.mp4", 1.5, 5.0, "Steep scenic descent toward the ocean"),
    ("20240601_143517_A.mp4", 2.0, 5.5, "Soaking in the warm summer sunshine"),
    # Act III: The Great Atlantic Surf & Beach
    ("20240601_121130.mp4", 2.0, 5.8, "Overlooking magnificent Downhill Strand"),
    ("20240601_124505.mp4", 2.5, 6.5, "Crashing Atlantic surf rolling onto shore"),
]


def create_polaroid_card(photo_path, title, subtitle, angle, out_png):
    """Render a high-resolution Polaroid card on a 1080x1920 transparent canvas with soft drop shadow."""
    raw_img = Image.open(photo_path)
    src = ImageOps.exif_transpose(raw_img).convert("RGB")
    
    photo_w, photo_h = 760, 920
    src_ratio = src.width / src.height
    target_ratio = photo_w / photo_h
    if src_ratio > target_ratio:
        new_w = int(src.height * target_ratio)
        src = src.crop(((src.width - new_w) // 2, 0, (src.width + new_w) // 2, src.height))
    else:
        new_h = int(src.width / target_ratio)
        src = src.crop((0, (src.height - new_h) // 2, src.width, (src.height + new_h) // 2))
    src = src.resize((photo_w, photo_h), Image.Resampling.LANCZOS)

    card_w, card_h = 840, 1140
    card = Image.new("RGBA", (card_w, card_h), (255, 255, 255, 255))
    card.paste(src, (40, 40))

    draw = ImageDraw.Draw(card)
    try:
        f_main = ImageFont.truetype(FONT_BOLD, 36)
        f_sub = ImageFont.truetype(FONT_REG, 22)
    except:
        f_main = f_sub = ImageFont.load_default()

    draw.text((46, 980), title, fill=(24, 24, 24, 255), font=f_main)
    draw.text((46, 1035), subtitle, fill=(115, 115, 115, 255), font=f_sub)

    # Accent color bar under card text
    draw.rectangle([46, 1085, 120, 1089], fill=(229, 169, 60, 255))

    # Rotate card with high-quality resampling
    rotated = card.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)

    # Canvas 1080x1920 with realistic soft drop shadow
    canvas = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    shadow_mask = Image.new("L", rotated.size, 0)
    shadow_mask.paste(rotated.split()[3])
    shadow_blur = shadow_mask.filter(ImageFilter.GaussianBlur(30))

    shadow_layer = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    px = (1080 - rotated.width) // 2
    py = (1920 - rotated.height) // 2 - 30

    shadow_color = Image.new("RGBA", rotated.size, (0, 0, 0, 160))
    shadow_layer.paste(shadow_color, (px + 6, py + 24), shadow_blur)

    canvas = Image.alpha_composite(canvas, shadow_layer)
    canvas.paste(rotated, (px, py), rotated)

    canvas.save(out_png, "PNG")
    print(f"  [Polaroid] Built {out_png.name} ('{title}')")


def render_photo_motion_segment(card_png, original_photo, duration=2.2, out_video=None):
    """Render motion graphic: blurred background + Ken Burns card zoom + 0.12s shutter flash."""
    # Ensure background photo is transposed correctly
    tmp_bg = out_video.parent / f"bg_{out_video.stem}.jpg"
    with Image.open(original_photo) as bg_img:
        bg_fixed = ImageOps.exif_transpose(bg_img).convert("RGB")
        bg_fixed.save(tmp_bg, quality=92)

    expr = (
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=24:3,eq=brightness=-0.14[bg];"
        f"[1:v]scale=eval=frame:w='1080*(1+0.03*t/{duration})':h='1920*(1+0.03*t/{duration})',crop=1080:1920[fg];"
        f"[bg][fg]overlay=0:0[comp];"
        f"[comp]fade=t=in:st=0:d=0.14:color=white[v]"
    )
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-loop", "1", "-t", f"{duration}", "-i", str(tmp_bg),
        "-loop", "1", "-t", f"{duration}", "-i", str(card_png),
        "-filter_complex", expr,
        "-map", "[v]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
        "-pix_fmt", "yuv420p", "-r", "24",
        "-t", f"{duration}",
        str(out_video)
    ]
    subprocess.run(cmd, check=True)
    tmp_bg.unlink(missing_ok=True)


def render_video_segment(src_path, start, end, out_path, lut_file=None):
    """Render video shot trimmed and conformed to 9:16 portrait (1080x1920) @ 24fps with Ken Burns drift."""
    dur = end - start
    zoom_expr = f"scale=eval=frame:w='1080*(1+0.022*t/{dur:.3f})':h='1920*(1+0.022*t/{dur:.3f})'"
    base_chain = (
        f"scale=1080:1920:force_original_aspect_ratio=increase,"
        f"crop=1080:1920:(iw-ow)/2:(ih-oh)/2,"
        f"{zoom_expr},"
        f"crop=1080:1920:(iw-ow)/2:(ih-oh)/2"
    )

    if lut_file and Path(lut_file).exists():
        color_filter = f"lut3d=file='{lut_file}'"
    else:
        color_filter = (
            "eq=contrast=1.06:brightness=0.03:saturation=1.08:gamma=1.05,"
            "curves=master='0/0.02 0.5/0.52 1/1'"
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


def build_reel_overlays(total_duration, shot_captions):
    """Generate kinetic typography, top progress bar, and intro/outro cards."""
    filters = []

    # 1. Top animated progress bar (gold accent)
    filters.append(
        f"drawbox=x=0:y=0:w='1080*(t/{total_duration:.3f})':h=8:color=0xE5A93C@1:t=fill"
    )

    # 2. Intro Title Card (0.4s - 3.8s with smooth fade)
    intro_start = 0.4
    intro_end = 3.8
    intro_alpha = f"if(between(t,{intro_start},{intro_end}),if(lt(t,{intro_start+0.4}),(t-{intro_start})/0.4,if(gt(t,{intro_end-0.4}),({intro_end}-t)/0.4,1)),0)"

    filters.append(
        f"drawbox=x=120:y=360:w=840:h=180:color=black@0.65:t=fill:enable='between(t,{intro_start},{intro_end})'"
    )
    filters.append(
        f"drawbox=x=115:y=360:w=6:h=180:color=0xE5A93C@0.95:t=fill:enable='between(t,{intro_start},{intro_end})'"
    )
    filters.append(
        f"drawtext=fontfile='{FONT_BOLD}':text='CASTLEROCK, UK':fontsize=52:fontcolor=white:x=150:y=390:alpha='{intro_alpha}'"
    )
    filters.append(
        f"drawtext=fontfile='{FONT_REG}':text='CAUSEWAY COASTAL ROUTE • NORTHERN IRELAND':fontsize=22:fontcolor=0xE0E0E0:x=152:y=465:alpha='{intro_alpha}'"
    )

    # 3. Dynamic Lower-third captions for key moments
    curr_time = 0.0
    for dur, caption in shot_captions:
        if caption:
            cap_start = curr_time + 0.3
            cap_end = curr_time + dur - 0.3
            if cap_end > cap_start + 0.6:
                cap_alpha = f"if(between(t,{cap_start:.2f},{cap_end:.2f}),if(lt(t,{cap_start+0.3:.2f}),(t-{cap_start:.2f})/0.3,if(gt(t,{cap_end-0.3:.2f}),({cap_end:.2f}-t)/0.3,1)),0)"
                filters.append(
                    f"drawbox=x=80:y=1640:w=920:h=90:color=black@0.60:t=fill:enable='between(t,{cap_start:.2f},{cap_end:.2f})'"
                )
                filters.append(
                    f"drawtext=fontfile='{FONT_BOLD}':text='{caption}':fontsize=30:fontcolor=white:x=(w-text_w)/2:y=1670:alpha='{cap_alpha}'"
                )
        curr_time += dur

    # 4. Outro Call-To-Action Card (Final 3.6s)
    outro_start = max(0.0, total_duration - 3.6)
    outro_alpha = f"if(between(t,{outro_start:.2f},{total_duration:.2f}),if(lt(t,{outro_start+0.4:.2f}),(t-{outro_start:.2f})/0.4,1),0)"

    filters.append(
        f"drawbox=x=120:y=780:w=840:h=230:color=black@0.75:t=fill:enable='between(t,{outro_start:.2f},{total_duration:.2f})'"
    )
    filters.append(
        f"drawbox=x=120:y=780:w=840:h=4:color=0xE5A93C@0.95:t=fill:enable='between(t,{outro_start:.2f},{total_duration:.2f})'"
    )
    filters.append(
        f"drawtext=fontfile='{FONT_BOLD}':text='NORTHERN IRELAND':fontsize=54:fontcolor=white:x=(w-text_w)/2:y=820:alpha='{outro_alpha}'"
    )
    filters.append(
        f"drawtext=fontfile='{FONT_REG}':text='Save this for your Causeway Coast trip 📍':fontsize=28:fontcolor=0xE5A93C:x=(w-text_w)/2:y=900:alpha='{outro_alpha}'"
    )

    # 5. Creator watermark bug (Bottom left)
    filters.append(
        f"drawtext=fontfile='{FONT_REG}':text='@castlerock.explore':fontsize=24:fontcolor=white@0.6:x=80:y=1820"
    )

    return ",".join(filters)


def generate_contact_sheet(video_path, output_png, num_frames=12):
    """Generate 12-frame contact sheet for QC verification."""
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
            "-vf", "scale=360:640", "-frames:v", "1", str(out_f)
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if out_f.exists():
            tmp_frames.append(out_f)

    if not tmp_frames:
        return

    cols = 4
    rows = (len(tmp_frames) + cols - 1) // cols
    w, h = 360, 640
    sheet = Image.new("RGB", (cols * w, rows * h), (15, 15, 15))
    draw = ImageDraw.Draw(sheet)

    for idx, frame_path in enumerate(tmp_frames):
        r = idx // cols
        c = idx % cols
        img = Image.open(frame_path)
        sheet.paste(img, (c * w, r * h))
        draw.rectangle([c * w, r * h + h - 35, c * w + w, r * h + h], fill=(0, 0, 0, 200))
        ts_val = timestamps[idx]
        draw.text((c * w + 15, r * h + h - 26), f"T = {ts_val:.1f}s", fill=(255, 255, 255))
        frame_path.unlink(missing_ok=True)

    sheet.save(output_png, quality=90)


def main():
    print("==================================================================")
    print("PRODUCING: CASTLEROCK, NORTHERN IRELAND (CATCHY INSTA REEL 9:16)")
    print("==================================================================")

    out_file = EDIT_DIR / "castlerock_insta_reel_9x16.mp4"
    qc_file = VERIFY_DIR / "qc_sheet_castlerock_reel.png"
    music_file = MUSIC_DIR / "solas_jamie_duffy.mp3"
    waves_sfx = ASSETS_DIR / "ambient_sfx" / "ocean_waves_crashing.mp3"

    tmp_dir = EDIT_DIR / "tmp_castlerock_build"
    tmp_dir.mkdir(exist_ok=True)
    cards_dir = tmp_dir / "cards"
    cards_dir.mkdir(exist_ok=True)

    # 1. Generate Polaroid Photo Cards
    print("\n[Step 1/5] Batch generating Polaroid Photo Cards with drop shadow...")
    built_cards = []
    for idx, (p_name, title, sub, angle) in enumerate(PHOTO_CARDS_DATA):
        p_path = CASTLEROCK_DIR / p_name
        card_png = cards_dir / f"card_{idx:02d}.png"
        create_polaroid_card(p_path, title, sub, angle, card_png)
        built_cards.append((card_png, p_path))

    # 2. Render Timeline Segments (Interweaving Video & Photo Snapshots)
    print("\n[Step 2/5] Conforming Video Clips and Rendering Motion Photo Cards...")
    timeline_segments = []
    shot_captions = []

    # Sequence Design:
    items_to_render = [
        ("video", VIDEO_SEGMENTS[0]),
        ("photo", (built_cards[0], 2.2, "Arriving at Platform 1")),
        ("video", VIDEO_SEGMENTS[1]),
        ("photo", (built_cards[1], 2.2, "Seaside coffee & artisan bakehouse")),
        ("video", VIDEO_SEGMENTS[2]),
        ("video", VIDEO_SEGMENTS[3]),
        ("photo", (built_cards[2], 2.4, "Golden sands of Downhill Strand")),
        ("video", VIDEO_SEGMENTS[4]),
        ("photo", (built_cards[3], 2.2, "Ancient Causeway basalt cliffs")),
        ("video", VIDEO_SEGMENTS[5]),
        ("photo", (built_cards[4], 2.2, "Spectacular coastal panoramic route")),
        ("video", VIDEO_SEGMENTS[6]),
    ]

    for idx, (item_type, item_data) in enumerate(items_to_render):
        seg_out = tmp_dir / f"seg_{idx:02d}.mp4"
        if item_type == "video":
            fn, st, en, cap = item_data
            v_src = CASTLEROCK_DIR / fn
            dur = en - st
            shot_captions.append((dur, cap))
            print(f"  [{idx+1}/{len(items_to_render)}] Video: {fn} ({dur:.1f}s)")
            render_video_segment(v_src, st, en, seg_out, lut_file=LUT_PATH)
        else:
            (card_png, orig_photo), dur, cap = item_data
            shot_captions.append((dur, cap))
            print(f"  [{idx+1}/{len(items_to_render)}] Motion Photo Card: {orig_photo.name} ({dur:.1f}s)")
            render_photo_motion_segment(card_png, orig_photo, duration=dur, out_video=seg_out)
        timeline_segments.append(seg_out)

    # 3. Concatenate Timeline Segments
    print("\n[Step 3/5] Concatenating timeline segments...")
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
    print(f"  Total timeline duration: {total_dur:.1f}s")

    # 4. Apply Kinetic Overlays, Progress Bar & Master Audio
    print("\n[Step 4/5] Applying kinetic overlays, progress bar & mastering audio...")
    overlay_filters = build_reel_overlays(total_dur, shot_captions)

    fade_out_st = max(0.0, total_dur - 3.0)
    audio_chain = (
        f"[1:a]atrim=0:{total_dur:.2f},afade=t=in:st=0:d=1.0,afade=t=out:st={fade_out_st:.2f}:d=3.0,volume=1.0[mus];"
        f"[2:a]aloop=loop=-1:size=2e+09,atrim=0:{total_dur:.2f},volume=0.22,afade=t=in:st=12:d=3.0[sfx];"
        f"[mus][sfx]amix=inputs=2:duration=first[amixed];"
        f"[amixed]loudnorm=I=-16:LRA=9:TP=-1.5[aout]"
    )

    mux_cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-i", str(raw_master),
        "-i", str(music_file),
        "-i", str(waves_sfx),
        "-filter_complex", f"[0:v]{overlay_filters}[vout];{audio_chain}",
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "256k",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-t", f"{total_dur:.2f}",
        str(out_file)
    ]
    subprocess.run(mux_cmd, check=True)
    print(f"  Exported deliverable: {out_file.name}")

    # 5. Visual QC Contact Sheet
    print("\n[Step 5/5] Generating Visual QC Contact Sheet...")
    generate_contact_sheet(out_file, qc_file)
    print(f"  QC Sheet: {qc_file.name}")

    # Cleanup tmp files
    shutil.rmtree(tmp_dir)

    print(f"\nSUCCESS: Finished Castlerock Reel -> {out_file}\n")


if __name__ == "__main__":
    main()
