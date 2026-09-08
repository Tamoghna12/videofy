"""
video_templates.presets - Standard presets for video production.
"""
from . import insta_catchy_reel
from . import cinematic_landscape
from . import lifestyle_vlog
from . import fast_cuts_short

PRESETS = {
    "insta_catchy_reel": insta_catchy_reel.render,
    "cinematic_landscape": cinematic_landscape.render,
    "lifestyle_vlog": lifestyle_vlog.render,
    "fast_cuts_short": fast_cuts_short.render,
}

__all__ = [
    "insta_catchy_reel",
    "cinematic_landscape",
    "lifestyle_vlog",
    "fast_cuts_short",
    "PRESETS",
]
