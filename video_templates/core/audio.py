"""
audio.py - Audio Mastering & Mixing Engine
Handles soundtrack resolution, ambient audio bed mixing,
smooth fade-ins/outs, and EBU R128 loudness normalization.
"""

from pathlib import Path

WORKSPACE_DIR = Path("/home/tamoghna/Documents/Video_editing")
MUSIC_DIR = WORKSPACE_DIR / "bg_music"
SFX_DIR = WORKSPACE_DIR / "assets" / "ambient_sfx"


def resolve_audio(name_or_path, is_sfx=False):
    """Resolve an audio file by filename or absolute path."""
    if not name_or_path:
        return None
    p = Path(name_or_path)
    if p.is_file():
        return p.resolve()
    
    search_dir = SFX_DIR if is_sfx else MUSIC_DIR
    if search_dir.exists():
        matches = list(search_dir.glob(f"**/*{name_or_path}*"))
        if matches:
            return matches[0].resolve()
    return None


def build_audio_filter(total_duration, music_volume=1.0, sfx_volume=0.20, target_lufs=-16):
    """
    Build FFmpeg audio filter complex string for:
    [1:a] Music track
    [2:a] Optional Ambient SFX track
    Outputs: [aout] mastered to target LUFS.
    """
    fade_st = max(0.0, total_duration - 3.5)
    
    music_chain = f"[1:a]atrim=0:{total_duration:.2f},afade=t=in:st=0:d=1.0,afade=t=out:st={fade_st:.2f}:d=3.5,volume={music_volume}[mus];"
    sfx_chain = f"[2:a]aloop=loop=-1:size=2e+09,atrim=0:{total_duration:.2f},volume={sfx_volume},afade=t=in:st=6:d=3.0[sfx];"
    mix_chain = "[mus][sfx]amix=inputs=2:duration=first[amixed];"
    norm_chain = f"[amixed]loudnorm=I={target_lufs}:LRA=9:TP=-1.5[aout]"

    return music_chain + sfx_chain + mix_chain + norm_chain
