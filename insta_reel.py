#!/usr/bin/env python3
"""
insta_reel.py - Automated Catchy Instagram Reel Video Generator
Combines raw video footage + batch-edited photo cards (Polaroid / Film Slide style)
with motion graphics, animated progress bar, and shutter transitions.

Designed for Antigravity with claudeclip & kinocut integration.
"""

import argparse
import json
import os
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

WORKSPACE_DIR = Path(__file__).resolve().parent
PHOTOS_DIR = WORKSPACE_DIR / "photos"
OUT_DIR = WORKSPACE_DIR / "edit"
VERIFY_DIR = OUT_DIR / "verify"

FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

# Color Grade for Photos & Video
PHOTO_GRADE = (
    "eq=contrast=1.06:brightness=0.03:gamma=1.06:saturation=0.96,"
    "colorbalance=rs=0.02:gs=0.0:bs=-0.02:rm=0.03:gm=0.01:bm=-0.01:rh=0.06:gh=0.02:bh=-0.04"
)


def batch_create_polaroid_cards(photo_list, out_dir):
    """Batch-style photos into high-res Polaroid cards with soft drop shadow."""
    out_dir.mkdir(parents=True, exist_ok=True)
    generated_cards = []

    for idx, (img_path, title, location, angle) in enumerate(photo_list):
        src = Image.open(img_path).convert("RGB")
        photo_w, photo_h = 760, 880
        src_ratio = src.width / src.height
        target_ratio = photo_w / photo_h
        if src_ratio > target_ratio:
            new_w = int(src.height * target_ratio)
            src = src.crop(((src.width - new_w) // 2, 0, (src.width + new_w) // 2, src.height))
        else:
            new_h = int(src.width / target_ratio)
            src = src.crop((0, (src.height - new_h) // 2, src.width, (src.height + new_h) // 2))
        src = src.resize((photo_w, photo_h), Image.Resampling.LANCZOS)

        card_w, card_h = 840, 1080
        card = Image.new("RGBA", (card_w, card_h), (255, 255, 255, 255))
        card.paste(src, (40, 40))

        draw = ImageDraw.Draw(card)
        try:
            f_main = ImageFont.truetype(FONT_BOLD, 36)
            f_sub = ImageFont.truetype(FONT_REG, 22)
        except:
            f_main = f_sub = ImageFont.load_default()

        draw.text((44, 940), title, fill=(25, 25, 25, 255), font=f_main)
        draw.text((44, 990), location, fill=(110, 110, 110, 255), font=f_sub)

        # Rotate with expansion
        rotated = card.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)

        # Build transparent 1080x1920 canvas with blurred drop shadow
        canvas = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
        shadow_mask = Image.new("L", rotated.size, 0)
        shadow_mask.paste(rotated.split()[3])
        shadow_blur = shadow_mask.filter(ImageFilter.GaussianBlur(28))

        shadow_layer = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
        px = (1080 - rotated.width) // 2
        py = (1920 - rotated.height) // 2

        shadow_color = Image.new("RGBA", rotated.size, (0, 0, 0, 175))
        shadow_layer.paste(shadow_color, (px + 6, py + 22), shadow_blur)

        canvas = Image.alpha_composite(canvas, shadow_layer)
        canvas.paste(rotated, (px, py), rotated)

        card_path = out_dir / f"card_{idx:02d}.png"
        canvas.save(card_path, "PNG")
        generated_cards.append((card_path, img_path))
        print(f"  [Photo Card] Created: {card_path.name} ('{title}')")

    return generated_cards


def render_photo_motion_segment(card_png, original_photo, duration=2.5, out_video=None):
    """Render an animated motion graphics clip: blurred ambient background + Ken Burns card zoom + shutter flash."""
    # Filter graph:
    # 1. Background: Original photo scaled to 1080x1920, heavy boxblur, slight dimming
    # 2. Foreground: Polaroid PNG drifting gently forward (zoom 1.00 -> 1.04)
    # 3. Flash: 0.12s white flash at entry (camera shutter emulation)
    expr = (
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:3,eq=brightness=-0.12[bg];"
        f"[1:v]scale=eval=frame:w='1080*(1+0.03*t/{duration})':h='1920*(1+0.03*t/{duration})',crop=1080:1920[fg];"
        f"[bg][fg]overlay=0:0[comp];"
        f"[comp]fade=t=in:st=0:d=0.15:color=white[v]"
    )
    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-loop", "1", "-t", f"{duration}", "-i", str(original_photo),
        "-loop", "1", "-t", f"{duration}", "-i", str(card_png),
        "-filter_complex", expr,
        "-map", "[v]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "19",
        "-pix_fmt", "yuv420p", "-r", "24",
        "-t", f"{duration}",
        str(out_video)
    ]
    subprocess.run(cmd, check=True)


def build_instagram_reel(video_segments, photo_cards, music_path, out_file, target_duration=60.0):
    """Weave live video clips and animated photo snapshots into a catchy Instagram Reel with progress bar."""
    tmp_dir = OUT_DIR / "tmp_reel_build"
    tmp_dir.mkdir(exist_ok=True)
    seg_files = []

    print("\n[1/4] Preparing timeline segments (interweaving video & photo snapshots)...")
    # Alternate between video clips and photo cards
    seg_idx = 0
    p_idx = 0
    for v_path, s_start, s_end in video_segments:
        # Extract live video segment
        v_seg = tmp_dir / f"seg_{seg_idx:02d}.mp4"
        v_dur = s_end - s_start
        cmd = [
            "ffmpeg", "-y", "-v", "error",
            "-ss", f"{s_start:.3f}", "-i", str(v_path), "-t", f"{v_dur:.3f}",
            "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,{PHOTO_GRADE}",
            "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "19",
            "-pix_fmt", "yuv420p", "-r", "24", str(v_seg)
        ]
        subprocess.run(cmd, check=True)
        seg_files.append(v_seg)
        seg_idx += 1

        # Every 2-3 video clips, insert an animated photo snapshot
        if seg_idx in (2, 5, 8) and p_idx < len(photo_cards):
            card_png, orig_img = photo_cards[p_idx]
            p_seg = tmp_dir / f"seg_{seg_idx:02d}_photo.mp4"
            render_photo_motion_segment(card_png, orig_img, duration=2.2, out_video=p_seg)
            seg_files.append(p_seg)
            seg_idx += 1
            p_idx += 1

    # Concatenate all
    print("\n[2/4] Stitching timeline segments...")
    concat_list = tmp_dir / "_reel_concat.txt"
    concat_list.write_text("".join(f"file '{p.resolve()}'\n" for p in seg_files))
    master_raw = tmp_dir / "reel_master_raw.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-f", "concat", "-safe", "0", "-i", str(concat_list),
        "-c", "copy", "-movflags", "+faststart", str(master_raw)
    ], check=True)

    # Read actual duration
    actual_dur = float(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(master_raw)
    ]).strip())

    print(f"\n[3/4] Adding Instagram Reel Motion Graphics (animated top progress bar & titles)...")
    # Kinetic motion graphics:
    # 1. Sleek top progress bar that animates from x=0 to x=1080 over actual_dur
    # 2. Instagram hashtag/handle tag: "@travel.yorkshire"
    # 3. Audio loudness normalization
    fade_st = max(0.0, actual_dur - 2.5)
    a_st = max(0.0, actual_dur - 3.5)

    progress_filter = (
        f"drawbox=x=0:y=18:w='1080*(t/{actual_dur:.2f})':h=8:color=0xffc83b@0.9:t=fill,"
        f"drawtext=fontfile={FONT_BOLD}:text='YORKSHIRE COAST • SNAPSHOTS':fontsize=28:fontcolor=white:"
        f"shadowcolor=black@0.6:shadowx=2:shadowy=2:x=(w-text_w)/2:y=50:alpha='if(lt(t,4),1,if(lt(t,5),5-t,0))',"
        f"drawtext=fontfile={FONT_REG}:text='@yorkshire.moments':fontsize=24:fontcolor=white@0.85:"
        f"shadowcolor=black@0.6:shadowx=2:shadowy=2:x=60:y=1820,"
        f"fade=t=out:st={fade_st:.2f}:d=2.5"
    )

    audio_filter = f"[1:a]atrim=0:{actual_dur:.2f},loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=out:st={a_st:.2f}:d=3.2[a]"

    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-i", str(master_raw),
        "-i", str(music_path),
        "-filter_complex", f"[0:v]{progress_filter}[v];{audio_filter}",
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "19",
        "-pix_fmt", "yuv420p", "-r", "24",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        "-t", f"{actual_dur:.2f}",
        str(out_file)
    ]
    subprocess.run(cmd, check=True)

    print(f"\n[4/4] Generating visual QC contact sheet...")
    qc_sheet = VERIFY_DIR / "qc_sheet_insta_reel.png"
    subprocess.run([
        "ffmpeg", "-y", "-v", "error",
        "-i", str(out_file),
        "-vf", "select='not(mod(n\\,75))',scale=270:480,tile=4x4",
        "-frames:v", "1", "-q:v", "2", str(qc_sheet)
    ], check=True)

    # Kinocut QC
    print("Running kinocut metric-qc audit...")
    cmd_qc = ["uvx", "--from", "kinocut", "kino", "--format", "json", "metric-qc", str(out_file)]
    subprocess.run(cmd_qc, capture_output=True, text=True)

    # Cleanup tmp
    for f in tmp_dir.glob("*"):
        f.unlink()
    tmp_dir.rmdir()

    print(f"\nSUCCESS! Catchy Instagram Reel generated: {out_file} ({actual_dur:.1f}s)")
    return out_file, qc_sheet


def main():
    print("=== Automated Instagram Reel Creator ===")
    photo_cards_data = [
        (PHOTOS_DIR / "whitby_abbey.jpg", "WHITBY ABBEY", "📍 NORTH YORKSHIRE", -3.5),
        (PHOTOS_DIR / "scarborough_bay.jpg", "SCARBOROUGH BAY", "📍 QUEEN OF THE COAST", 3.0),
        (PHOTOS_DIR / "york_shambles.jpg", "THE SHAMBLES", "📍 HISTORIC YORK", -2.5)
    ]

    cards = batch_create_polaroid_cards(photo_cards_data, OUT_DIR / "cards")

    # Dynamic video segments chosen from Whitby, Scarborough, and York
    def find_clip(stem):
        matches = list(WORKSPACE_DIR.glob(f"**/{stem}.mp4"))
        if not matches:
            raise FileNotFoundError(f"Clip {stem} not found")
        return matches[0]

    video_segments = [
        (find_clip("20260906_105056"), 1.5, 4.5),
        (find_clip("20260906_134022"), 12.0, 15.5),
        (find_clip("20260905_160428"), 3.0, 6.5),
        (find_clip("20260905_184406"), 29.0, 33.5),
        (find_clip("20260903_121155"), 2.0, 5.5),
        (find_clip("20260903_183008"), 4.0, 8.5),
        (find_clip("20260906_154424"), 0.5, 4.0),
    ]

    music = WORKSPACE_DIR / "bg_music/memory_reboot.mp3"
    out_video = OUT_DIR / "catchy_insta_reel_9x16.mp4"

    build_instagram_reel(video_segments, cards, music, out_video)


if __name__ == "__main__":
    main()
