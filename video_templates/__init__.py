"""
video_templates - Universal Modular Video Template Engine with AI Beat Sync,
Dynamic Smart Cropping, and Multi-Vendor GPU Hardware Acceleration.
"""
from .presets import PRESETS
from .mcp_bridge import probe_media, validate_deliverable
from .core.accel import detect_hardware_encoder, get_hardware_info
from .core.beat_sync import detect_beats, snap_timeline_to_beats
from .core.smart_crop import calculate_smart_crop

__version__ = "1.1.0"
__all__ = [
    "PRESETS",
    "probe_media",
    "validate_deliverable",
    "detect_hardware_encoder",
    "get_hardware_info",
    "detect_beats",
    "snap_timeline_to_beats",
    "calculate_smart_crop",
]
