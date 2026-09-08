"""
audio.py - Audio Mastering & Mixing Engine
Handles soundtrack resolution, ambient audio bed mixing,
smooth fade-ins/outs, and EBU R128 loudness normalization.
"""

import json
from pathlib import Path

WORKSPACE_DIR = Path("/home/tamoghna/Documents/Video_editing")
AUDIO_LIB_DIR = WORKSPACE_DIR / "assets" / "audio"
AUDIO_SFX_DIR = AUDIO_LIB_DIR / "sfx"
AUDIO_BGM_DIR = AUDIO_LIB_DIR / "bg_music"
LEGACY_MUSIC_DIR = WORKSPACE_DIR / "bg_music"
LEGACY_SFX_DIR = WORKSPACE_DIR / "assets" / "ambient_sfx"


def get_audio_manifest():
    """Load the comprehensive audio library manifest with metadata & licenses."""
    manifest_path = AUDIO_LIB_DIR / "manifest.json"
    if manifest_path.is_file():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"sfx": [], "bg_music": []}


def resolve_audio(name_or_path, is_sfx=False):
    """
    Resolve an audio file by filename, relative path, or stem ID.
    Searches assets/audio library first, then falls back to legacy directories.
    """
    if not name_or_path:
        return None
    p = Path(name_or_path)
    if p.is_file():
        return p.resolve()
    
    stem = p.stem.lower()
    
    # Priority directories depending on is_sfx
    if is_sfx:
        search_dirs = [AUDIO_SFX_DIR, LEGACY_SFX_DIR, AUDIO_BGM_DIR, LEGACY_MUSIC_DIR]
    else:
        search_dirs = [AUDIO_BGM_DIR, LEGACY_MUSIC_DIR, AUDIO_SFX_DIR, LEGACY_SFX_DIR]

    for s_dir in search_dirs:
        if not s_dir.exists():
            continue
        # Exact stem or filename match
        for f in s_dir.glob("**/*"):
            if f.is_file() and (f.name.lower() == name_or_path.lower() or f.stem.lower() == stem):
                return f.resolve()
        # Partial match
        matches = list(s_dir.glob(f"**/*{stem}*"))
        for m in matches:
            if m.is_file() and m.suffix.lower() in [".mp3", ".wav", ".ogg", ".aac", ".m4a", ".flac"]:
                return m.resolve()
                
    return None


def list_audio_items(kind="all", category=None):
    """
    Return filtered list of audio items from manifest or disk.
    kind: 'music', 'sfx', or 'all'
    category: optional filter like 'transitions', 'foley_ui', 'travel_upbeat', etc.
    """
    manifest = get_audio_manifest()
    results = []

    if kind in ["music", "all"]:
        for item in manifest.get("bg_music", []):
            if not category or category.lower() in item.get("category", "").lower():
                entry = dict(item)
                entry["type"] = "music"
                results.append(entry)

    if kind in ["sfx", "all"]:
        for item in manifest.get("sfx", []):
            if not category or category.lower() in item.get("category", "").lower():
                entry = dict(item)
                entry["type"] = "sfx"
                results.append(entry)

    return results


def build_audio_filter(
    total_duration,
    music_volume=1.0,
    sfx_volume=0.20,
    target_lufs=-16,
    has_sfx=True,
    voiceover_duration=None,
    voiceover_start=1.5
):
    """
    Build FFmpeg audio filter complex string for:
    [1:a] Music track (with automatic ducking when voiceover is active)
    [2:a] Optional Ambient SFX track
    [3:a] Optional Voiceover track (delayed and boosted for dialogue clarity)
    Outputs: [aout] mastered to target LUFS.
    """
    fade_st = max(0.0, total_duration - 3.5)
    
    # Check if voiceover is included
    if voiceover_duration and voiceover_duration > 0:
        d_in = max(0.0, voiceover_start - 0.25)
        d_out = min(total_duration, voiceover_start + voiceover_duration + 0.6)
        duck_vol = 0.22 * music_volume
        vol_expr = f"if(between(t,{d_in:.2f},{d_out:.2f}),{duck_vol:.2f},{music_volume:.2f})"
        
        music_chain = (
            f"[1:a]atrim=0:{total_duration:.2f},"
            f"afade=t=in:st=0:d=1.0,afade=t=out:st={fade_st:.2f}:d=3.5,"
            f"volume=eval=frame:volume='{vol_expr}'[mus];"
        )
        
        vox_idx = 3 if has_sfx else 2
        delay_ms = int(voiceover_start * 1000)
        vox_chain = f"[{vox_idx}:a]adelay={delay_ms}|{delay_ms},volume=1.35[vox];"
        
        if has_sfx:
            sfx_chain = f"[2:a]aloop=loop=-1:size=2e+09,atrim=0:{total_duration:.2f},volume={sfx_volume},afade=t=in:st=4:d=2.0[sfx];"
            mix_chain = "[mus][sfx][vox]amix=inputs=3:duration=first[amixed];"
            chains = music_chain + sfx_chain + vox_chain + mix_chain
        else:
            mix_chain = "[mus][vox]amix=inputs=2:duration=first[amixed];"
            chains = music_chain + vox_chain + mix_chain
            
    else:
        # Standard music + optional sfx mixing
        music_chain = f"[1:a]atrim=0:{total_duration:.2f},afade=t=in:st=0:d=1.0,afade=t=out:st={fade_st:.2f}:d=3.5,volume={music_volume}[mus];"
        if has_sfx:
            sfx_chain = f"[2:a]aloop=loop=-1:size=2e+09,atrim=0:{total_duration:.2f},volume={sfx_volume},afade=t=in:st=6:d=3.0[sfx];"
            mix_chain = "[mus][sfx]amix=inputs=2:duration=first[amixed];"
            chains = music_chain + sfx_chain + mix_chain
        else:
            mix_chain = "[mus]anull[amixed];"
            chains = music_chain + mix_chain

    norm_chain = f"[amixed]loudnorm=I={target_lufs}:LRA=9:TP=-1.5[aout]"
    return chains + norm_chain
