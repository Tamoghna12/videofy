"""
grading.py - Color Grading and LUT Resolver
Resolves 3D LUT cubes and provides calibrated tone curves
for video and photo conforming.
"""

from pathlib import Path

WORKSPACE_DIR = Path("/home/tamoghna/Documents/Video_editing")
LUTS_DIR = WORKSPACE_DIR / "assets" / "luts"


PRESET_GRADES = {
    "odyssey": (
        "curves=master='0/0 0.15/0.17 0.5/0.53 0.85/0.87 1/0.98',"
        "colorbalance=rs=-0.01:gs=0.0:bs=0.02:rm=0.0:gm=0.01:bm=0.02:rh=0.0:gh=0.0:bh=0.01,"
        "eq=contrast=1.06:brightness=0.01:saturation=1.08:gamma=1.02,"
        "cas=0.30"
    ),
    "summer_vibrant": "eq=contrast=1.06:brightness=0.03:saturation=1.14:gamma=1.04,curves=master='0/0.02 0.5/0.52 1/1'",
    "culinary_warm": "eq=contrast=1.06:brightness=0.03:saturation=1.08:gamma=1.06,curves=master='0/0.02 0.5/0.52 1/1'",
    "clean_landscape": "curves=master='0/0.04 0.2/0.30 0.5/0.56 0.8/0.82 1/0.97',eq=contrast=1.03:brightness=0.035:gamma=1.14:saturation=1.10",
    "bright_landscape": "curves=master='0/0.05 0.25/0.38 0.5/0.62 0.75/0.86 1/1',eq=contrast=1.03:brightness=0.06:gamma=1.20:saturation=1.16",
    "moody_contrast": "eq=contrast=1.12:brightness=-0.02:saturation=0.92:gamma=0.98,curves=master='0/0 0.25/0.22 0.75/0.78 1/1'",
}


def resolve_lut(lut_name_or_path):
    """Resolve a LUT by full path, relative path, or partial filename match."""
    if not lut_name_or_path:
        return None
    p = Path(lut_name_or_path)
    if p.is_file():
        return p.resolve()
    if LUTS_DIR.exists():
        matches = list(LUTS_DIR.glob(f"**/*{lut_name_or_path}*"))
        if matches:
            return matches[0].resolve()
    return None


def get_color_filter(grade_type="summer_vibrant", lut_name=None):
    """
    Returns the FFmpeg video filter snippet for color grading.
    Provides calibrated tone curves, color balance and filmic color rendering.
    """
    if grade_type == "odyssey":
        return PRESET_GRADES["odyssey"]

    lut_file = resolve_lut(lut_name)
    if lut_file:
        escaped_path = str(lut_file).replace("\\", "/").replace(":", "\\:")
        return f"lut3d=file='{escaped_path}'"
    
    if grade_type in PRESET_GRADES:
        return PRESET_GRADES[grade_type]
    
    return "eq=contrast=1.04:brightness=0.02:saturation=1.05"
