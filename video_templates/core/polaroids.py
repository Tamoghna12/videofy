"""
polaroids.py - Batch Polaroid and Photo Card Generator
Generates high-res styled photo cards with EXIF transposition,
soft drop shadows, and animated motion graphics segments.
"""

import subprocess
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageFilter

FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"


def create_polaroid_card(photo_path, title, subtitle, angle, out_png, canvas_size=(1080, 1920)):
    """Render a Polaroid card on a transparent canvas with realistic soft drop shadow."""
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
    draw.rectangle([46, 1085, 130, 1089], fill=(229, 169, 60, 255))

    rotated = card.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)

    cw, ch = canvas_size
    canvas = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    shadow_mask = Image.new("L", rotated.size, 0)
    shadow_mask.paste(rotated.split()[3])
    shadow_blur = shadow_mask.filter(ImageFilter.GaussianBlur(30))

    shadow_layer = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    px = (cw - rotated.width) // 2
    py = (ch - rotated.height) // 2 - 30

    shadow_color = Image.new("RGBA", rotated.size, (0, 0, 0, 160))
    shadow_layer.paste(shadow_color, (px + 6, py + 24), shadow_blur)

    canvas = Image.alpha_composite(canvas, shadow_layer)
    canvas.paste(rotated, (px, py), rotated)

    out_png.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_png, "PNG")
    return out_png


def render_photo_motion_segment(card_png, original_photo, duration=2.4, out_video=None, canvas_res="1080x1920", fps=24):
    """Render motion graphic: blurred photo background + Ken Burns card drift + 0.14s shutter flash."""
    w, h = [int(x) for x in canvas_res.split("x")]
    tmp_bg = out_video.parent / f"bg_{out_video.stem}.jpg"
    with Image.open(original_photo) as bg_img:
        bg_fixed = ImageOps.exif_transpose(bg_img).convert("RGB")
        bg_fixed.save(tmp_bg, quality=92)

    expr = (
        f"[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},boxblur=24:3,eq=brightness=-0.14[bg];"
        f"[1:v]scale=eval=frame:w='{w}*(1+0.03*t/{duration})':h='{h}*(1+0.03*t/{duration})',crop={w}:{h}[fg];"
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
        "-pix_fmt", "yuv420p", "-r", str(fps),
        "-t", f"{duration}",
        str(out_video)
    ]
    subprocess.run(cmd, check=True)
    tmp_bg.unlink(missing_ok=True)
    return out_video
