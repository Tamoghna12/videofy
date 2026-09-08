"""
video_templates.core - Core modular engine for video conforming, grading, polaroids, overlays,
audio mastering, GPU hardware acceleration, AI beat synchronization, and smart cropping.
"""
from .conformer import conform_clip
from .polaroids import create_polaroid_card, render_photo_motion_segment
from .grading import get_color_filter, resolve_lut
from .overlays import build_timeline_overlays, clean_text
from .audio import resolve_audio, build_audio_filter
from .qc import generate_contact_sheet
from .accel import detect_hardware_encoder, get_encoder_args, get_hardware_info
from .beat_sync import detect_beats, snap_timeline_to_beats
from .smart_crop import calculate_smart_crop, get_crop_filter_expression

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
    "detect_hardware_encoder",
    "get_encoder_args",
    "get_hardware_info",
    "detect_beats",
    "snap_timeline_to_beats",
    "calculate_smart_crop",
    "get_crop_filter_expression",
]
