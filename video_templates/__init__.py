"""
video_templates - Universal Modular Video Template Engine.
"""
from .presets import PRESETS
from .mcp_bridge import probe_media, validate_deliverable

__version__ = "1.0.0"
__all__ = ["PRESETS", "probe_media", "validate_deliverable"]
