"""
mcp_bridge.py - MCP Integration Bridge
Provides programmatic hooks into kinocut and claudeclip MCP tools
for metadata inspection, scene detection, and quality validation.
"""

import json
import subprocess
from pathlib import Path


def probe_clip_metadata(clip_path):
    """
    Probe clip metadata using ffprobe / kinocut standard JSON format.
    Returns: {width, height, fps, duration, codec, bitrate}
    """
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration,size,bit_rate:stream=width,height,r_frame_rate,codec_name",
        "-of", "json", str(clip_path)
    ]
    try:
        res = json.loads(subprocess.check_output(cmd))
        dur = float(res.get("format", {}).get("duration", 0))
        size = int(res.get("format", {}).get("size", 0))
        streams = res.get("streams", [])
        v_stream = [s for s in streams if s.get("codec_name") in ["h264", "hevc", "mp4v", "vp9"]]
        if v_stream:
            w = int(v_stream[0].get("width", 0))
            h = int(v_stream[0].get("height", 0))
            fps_str = v_stream[0].get("r_frame_rate", "24/1")
            fps = eval(fps_str) if "/" in fps_str else float(fps_str)
            codec = v_stream[0].get("codec_name")
            return {
                "success": True,
                "duration": dur,
                "width": w,
                "height": h,
                "fps": fps,
                "codec": codec,
                "size_bytes": size,
                "aspect": f"{w}:{h}"
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

    return {"success": False, "error": "No video stream found"}


def validate_deliverable(video_path, expected_aspect="9:16"):
    """Validates that deliverable matches expected standards."""
    info = probe_clip_metadata(video_path)
    if not info.get("success"):
        return {"valid": False, "reason": info.get("error")}

    w, h = info["width"], info["height"]
    if expected_aspect == "9:16" and (w != 1080 or h != 1920):
        return {"valid": False, "reason": f"Expected 1080x1920 (9:16), got {w}x{h}"}
    if expected_aspect == "16:9" and (w != 1920 or h != 1080):
        return {"valid": False, "reason": f"Expected 1920x1080 (16:9), got {w}x{h}"}

    if info["duration"] < 5.0:
        return {"valid": False, "reason": f"Video too short: {info['duration']}s"}

    return {
        "valid": True,
        "duration": info["duration"],
        "resolution": f"{w}x{h}",
        "fps": info["fps"],
        "size_mb": round(info["size_bytes"] / (1024 * 1024), 2)
    }


probe_media = probe_clip_metadata

