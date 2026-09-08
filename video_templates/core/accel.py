"""
accel.py - Multi-Vendor GPU Hardware Acceleration Engine
Supports NVIDIA NVENC, Intel Arc QSV, Apple Silicon VideoToolbox, Linux VAAPI, and CPU fallback.
"""

import subprocess
import sys


_ENCODER_CACHE = {}


def test_encoder(encoder_name, extra_args=None):
    """Test if an FFmpeg encoder is functional on the current hardware."""
    cmd = [
        "ffmpeg", "-v", "error",
        "-f", "lavfi", "-i", "color=s=320x240:d=0.1",
        "-c:v", encoder_name,
    ]
    if extra_args:
        cmd.extend(extra_args)
    cmd.extend(["-f", "null", "-"])

    try:
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        return res.returncode == 0
    except Exception:
        return False


def detect_hardware_encoder(preference="auto"):
    """
    Detects the best available hardware video encoder.
    preference: 'auto', 'nvenc', 'qsv', 'videotoolbox', 'vaapi', 'cpu'
    """
    if preference in _ENCODER_CACHE:
        return _ENCODER_CACHE[preference]

    if preference == "cpu":
        _ENCODER_CACHE[preference] = ("libx264", "cpu")
        return _ENCODER_CACHE[preference]

    # Explicit requests
    if preference == "nvenc":
        if test_encoder("h264_nvenc"):
            _ENCODER_CACHE[preference] = ("h264_nvenc", "nvenc")
            return _ENCODER_CACHE[preference]
    elif preference == "qsv":
        if test_encoder("h264_qsv"):
            _ENCODER_CACHE[preference] = ("h264_qsv", "qsv")
            return _ENCODER_CACHE[preference]
    elif preference == "videotoolbox":
        if test_encoder("h264_videotoolbox"):
            _ENCODER_CACHE[preference] = ("h264_videotoolbox", "videotoolbox")
            return _ENCODER_CACHE[preference]
    elif preference == "vaapi":
        if test_encoder("h264_vaapi"):
            _ENCODER_CACHE[preference] = ("h264_vaapi", "vaapi")
            return _ENCODER_CACHE[preference]

    # 'auto' auto-probing in order of performance
    # 1. NVIDIA NVENC
    if test_encoder("h264_nvenc"):
        _ENCODER_CACHE["auto"] = ("h264_nvenc", "nvenc")
        return _ENCODER_CACHE["auto"]

    # 2. Intel Arc / Quick Sync Video (QSV)
    if test_encoder("h264_qsv"):
        _ENCODER_CACHE["auto"] = ("h264_qsv", "qsv")
        return _ENCODER_CACHE["auto"]

    # 3. Apple Silicon VideoToolbox
    if sys.platform == "darwin" and test_encoder("h264_videotoolbox"):
        _ENCODER_CACHE["auto"] = ("h264_videotoolbox", "videotoolbox")
        return _ENCODER_CACHE["auto"]

    # 4. Linux VAAPI
    if test_encoder("h264_vaapi"):
        _ENCODER_CACHE["auto"] = ("h264_vaapi", "vaapi")
        return _ENCODER_CACHE["auto"]

    # 5. CPU Fallback
    _ENCODER_CACHE["auto"] = ("libx264", "cpu")
    return _ENCODER_CACHE["auto"]


def get_encoder_args(preference="auto", crf=19, is_segment=False):
    """
    Returns an array of FFmpeg command-line arguments for video encoding.
    """
    encoder, accel_type = detect_hardware_encoder(preference)

    if accel_type == "nvenc":
        # NVIDIA NVENC settings
        preset = "p2" if is_segment else "p4"
        return [
            "-c:v", "h264_nvenc",
            "-preset", preset,
            "-cq", str(crf),
            "-pix_fmt", "yuv420p"
        ]

    elif accel_type == "qsv":
        # Intel Arc / Quick Sync Video settings
        preset = "veryfast" if is_segment else "medium"
        return [
            "-c:v", "h264_qsv",
            "-preset", preset,
            "-global_quality", str(crf + 1),
            "-pix_fmt", "nv12"
        ]

    elif accel_type == "videotoolbox":
        # Apple Silicon VideoToolbox settings
        return [
            "-c:v", "h264_videotoolbox",
            "-q:v", "65",
            "-pix_fmt", "yuv420p"
        ]

    elif accel_type == "vaapi":
        # VAAPI settings
        return [
            "-c:v", "h264_vaapi",
            "-qp", str(crf),
        ]

    else:
        # Standard CPU x264
        preset = "veryfast" if is_segment else "medium"
        return [
            "-c:v", "libx264",
            "-preset", preset,
            "-crf", str(crf),
            "-pix_fmt", "yuv420p"
        ]


def get_hardware_info():
    """Returns a dictionary summary of hardware acceleration support on the system."""
    encoders = {
        "h264_nvenc (NVIDIA)": test_encoder("h264_nvenc"),
        "h264_qsv (Intel Arc / QuickSync)": test_encoder("h264_qsv"),
        "h264_videotoolbox (Apple Silicon)": test_encoder("h264_videotoolbox") if sys.platform == "darwin" else False,
        "h264_vaapi (Linux VAAPI)": test_encoder("h264_vaapi"),
        "libx264 (Universal CPU)": test_encoder("libx264"),
    }
    active_enc, active_type = detect_hardware_encoder("auto")
    return {
        "active_encoder": active_enc,
        "acceleration_type": active_type,
        "available_encoders": encoders
    }
