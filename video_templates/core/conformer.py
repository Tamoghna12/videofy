"""
conformer.py - Video conforming engine
Handles 9:16 portrait and 16:9 landscape video scaling, aspect crop,
AI smart-cropping auto-framing, Ken Burns camera motion, and hardware acceleration.
"""

import json
import subprocess
from pathlib import Path
from .accel import get_encoder_args
from .smart_crop import calculate_smart_crop, get_crop_filter_expression


def probe_clip_dimensions(clip_path):
    """Returns width and height of video file."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "stream=width,height",
        "-of", "json", str(clip_path)
    ]
    try:
        data = json.loads(subprocess.check_output(cmd))
        s = data["streams"][0]
        return int(s.get("width", 1920)), int(s.get("height", 1080))
    except Exception:
        return 1920, 1080


def conform_clip(
    src_path,
    start,
    end,
    out_path,
    target_res="1080x1920",
    fps=24,
    color_filter=None,
    zoom_rate=0.022,
    accel="auto",
    smart_crop=False
):
    """
    Conforms a video segment to target resolution with Ken Burns motion,
    optional AI smart-crop subject tracking, and GPU hardware acceleration.
    """
    w, h = [int(x) for x in target_res.split("x")]
    dur = max(0.1, end - start)

    # 1. Aspect cropping & AI smart-crop
    if smart_crop:
        orig_w, orig_h = probe_clip_dimensions(src_path)
        focal_start, focal_end = calculate_smart_crop(src_path, start, end, orig_w, orig_h, w, h)
        crop_expr = get_crop_filter_expression(orig_w, orig_h, w, h, focal_start, focal_end, dur)
    else:
        crop_expr = f"crop={w}:{h}:(iw-ow)/2:(ih-oh)/2"

    # 2. Ken Burns push-in scale expression
    zoom_expr = f"scale=eval=frame:w='{w}*(1+{zoom_rate}*t/{dur:.3f})':h='{h}*(1+{zoom_rate}*t/{dur:.3f})'"
    base_filter = (
        f"scale={w}:{h}:force_original_aspect_ratio=increase,"
        f"{crop_expr},"
        f"{zoom_expr},"
        f"crop={w}:{h}:(iw-ow)/2:(ih-oh)/2"
    )

    if color_filter:
        vf = f"{base_filter},{color_filter}"
    else:
        vf = base_filter

    # 3. Hardware acceleration encoder flags
    enc_args = get_encoder_args(preference=accel, crf=19, is_segment=True)

    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-hwaccel", "d3d11va",
        "-ss", f"{start:.3f}",
        "-i", str(src_path),
        "-t", f"{dur:.3f}",
        "-vf", vf,
        "-r", str(fps),
    ]
    cmd.extend(enc_args)
    cmd.extend(["-an", str(out_path)])

    subprocess.run(cmd, check=True)
    return out_path
