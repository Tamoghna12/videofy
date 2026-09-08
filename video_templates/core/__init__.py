"""
video_templates.core - Core modular engine for video conforming, grading, polaroids, overlays, and audio mastering.
"""
from .conformer import conform_clip
from .polaroids import create_polaroid_card, render_photo_motion_segment
from .grading import get_color_filter, resolve_lut
from .overlays import build_timeline_overlays, clean_text
from .audio import resolve_audio, build_audio_filter
from .qc import generate_contact_sheet

__all__ = [
    "conform_clip",
    "create_polaroid_card",
    "render_photo_motion_segment",
    "get_color_filter",
    "resolve_lut",
    "build_timeline_overlays",
    "clean_text",
    "resolve_audio",
    "build_audio_filter",
    "generate_contact_sheet",
]
