"""
qc.py - Automated Visual QC Contact Sheet Generator
Samples evenly spaced frames across the timeline and renders
a clean multi-frame contact sheet for rapid verification.
"""

import subprocess
from pathlib import Path
from PIL import Image, ImageDraw


def generate_contact_sheet(video_path, output_png, num_frames=12, aspect="9:16"):
    """
    Generate an evenly-spaced multi-frame contact sheet from a video deliverable.
    aspect: '9:16' (vertical thumbnails) or '16:9' (widescreen thumbnails)
    """
    video_path = Path(video_path)
    output_png = Path(output_png)
    output_png.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir = output_png.parent / f"_tmp_qc_{video_path.stem}"
    tmp_dir.mkdir(exist_ok=True)

    probe_cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video_path)
    ]
    dur = float(subprocess.check_output(probe_cmd).strip())
    timestamps = [dur * (i + 0.5) / num_frames for i in range(num_frames)]

    is_portrait = (aspect == "9:16")
    tw, th = (270, 480) if is_portrait else (480, 270)

    tmp_frames = []
    for i, ts in enumerate(timestamps):
        out_f = tmp_dir / f"frame_{i:02d}.jpg"
        cmd = [
            "ffmpeg", "-y", "-ss", f"{ts:.3f}", "-i", str(video_path),
            "-vf", f"scale={tw}:{th}", "-frames:v", "1", str(out_f)
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if out_f.exists():
            tmp_frames.append(out_f)

    if not tmp_frames:
        return None

    cols = 4
    rows = (len(tmp_frames) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * th), (15, 15, 15))
    draw = ImageDraw.Draw(sheet)

    for idx, frame_path in enumerate(tmp_frames):
        r = idx // cols
        c = idx % cols
        img = Image.open(frame_path)
        sheet.paste(img, (c * tw, r * th))
        draw.rectangle([c * tw, r * th + th - 28, c * tw + tw, r * th + th], fill=(0, 0, 0, 200))
        ts_val = timestamps[idx]
        draw.text((c * tw + 10, r * th + th - 20), f"T = {ts_val:.1f}s", fill=(255, 255, 255))

    sheet.save(output_png, quality=90)
    
    # Clean up temp frames
    for f in tmp_frames:
        f.unlink(missing_ok=True)
    tmp_dir.rmdir()

    return output_png
