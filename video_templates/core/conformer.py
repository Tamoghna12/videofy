"""
conformer.py - Video conforming engine
Handles 9:16 portrait and 16:9 landscape video scaling, aspect crop,
and subtle Ken Burns camera motion (push-in / drift).
"""

import subprocess
from pathlib import Path


def conform_clip(src_path, start, end, out_path, target_res="1080x1920", fps=24, color_filter=None, zoom_rate=0.022):
    """
    Conforms a video segment to target resolution with subtle push-in.
    target_res: '1080x1920' (9:16) or '1920x1080' (16:9)
    """
    w, h = [int(x) for x in target_res.split("x")]
    dur = end - start

    # Smooth Ken Burns push-in scale expression
    zoom_expr = f"scale=eval=frame:w='{w}*(1+{zoom_rate}*t/{dur:.3f})':h='{h}*(1+{zoom_rate}*t/{dur:.3f})'"
    base_filter = (
        f"scale={w}:{h}:force_original_aspect_ratio=increase,"
        f"crop={w}:{h}:(iw-ow)/2:(ih-oh)/2,"
        f"{zoom_expr},"
        f"crop={w}:{h}:(iw-ow)/2:(ih-oh)/2"
    )

    if color_filter:
        vf = f"{base_filter},{color_filter}"
    else:
        vf = base_filter

    cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-ss", f"{start:.3f}",
        "-i", str(src_path),
        "-t", f"{dur:.3f}",
        "-vf", vf,
        "-r", str(fps),
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "19",
        "-pix_fmt", "yuv420p",
        "-an",
        str(out_path)
    ]
    subprocess.run(cmd, check=True)
    return out_path
