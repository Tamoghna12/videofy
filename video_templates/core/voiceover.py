"""
voiceover.py - AI Zero-Shot Cloned Voiceover Engine
Bridges Videofy with the local Qwen3-TTS 0.6B GPU service in the 'kitten'
environment to synthesize personalized narration using your cloned voice sample.
"""

import os
import json
import subprocess
import tempfile
from pathlib import Path

# Paths to the kitten environment and science_vids voice cloning assets
KITTEN_PYTHON = Path("/home/tamoghna/anaconda3/envs/kitten/bin/python")
SCIENCE_VIDS_DIR = Path("/home/tamoghna/Documents/sci_tech/science_vids")
DEFAULT_REF_AUDIO = SCIENCE_VIDS_DIR / "assets" / "tee_voice_16k.wav"


def is_voiceover_available() -> bool:
    """Check if the local voice cloning environment and voice sample are available."""
    return KITTEN_PYTHON.is_file() and DEFAULT_REF_AUDIO.is_file()


def get_audio_duration(audio_path: Path) -> float:
    """Get the exact duration in seconds of an audio file via ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "csv=p=0",
        str(audio_path)
    ]
    res = subprocess.check_output(cmd).decode("utf-8").strip()
    return float(res)


def generate_voiceover(
    text: str,
    output_path: Path = None,
    speed: float = 1.15,
    reference_audio: Path = None
) -> dict:
    """
    Synthesize narrative voiceover using Qwen3-TTS zero-shot voice cloning on GPU.
    
    Args:
        text: The narration text to synthesize.
        output_path: Destination .wav path. If None, a temp file is created.
        speed: Speech tempo factor (default: 1.15 for natural, engaging pace).
        reference_audio: Path to the reference voice clip. Defaults to tee_voice_16k.wav.
        
    Returns:
        dict: {"audio_file": Path, "duration": float, "text": str}
    """
    if not is_voiceover_available():
        raise RuntimeError(
            f"Voice cloning environment not ready. Ensure {KITTEN_PYTHON} and {DEFAULT_REF_AUDIO} exist."
        )

    ref_audio = Path(reference_audio) if reference_audio else DEFAULT_REF_AUDIO
    if not ref_audio.is_file():
        raise FileNotFoundError(f"Reference voice audio not found: {ref_audio}")

    if output_path is None:
        fd, tmp_file = tempfile.mkstemp(suffix="_voiceover.wav", prefix="videofy_")
        os.close(fd)
        output_path = Path(tmp_file)
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n🎙️ Synthesizing Cloned Voiceover ({len(text)} chars, speed={speed:.2f}x)...")
    print(f"  📝 Narration: \"{text}\"")
    print(f"  🗣️ Voice Profile: {ref_audio.name}")

    # Python runner code executed within the kitten conda environment
    runner_code = f"""
import sys, os
sys.path.append({json.dumps(str(SCIENCE_VIDS_DIR))})
from core.qwen_tts_service import QwenTTSService

text = {json.dumps(text)}
out_path = {json.dumps(str(output_path))}
ref_audio = {json.dumps(str(ref_audio))}
speed = {float(speed)}

service = QwenTTSService(reference_audio=ref_audio, speed=speed)
res = service.generate_from_text(text, path=out_path)
print("VOICEOVER_SUCCESS")
"""

    env = os.environ.copy()
    # Strip any conflicting conda variables
    for k in ["CONDA_PREFIX", "CONDA_DEFAULT_ENV", "CONDA_PROMPT_MODIFIER", "PYTHONPATH"]:
        env.pop(k, None)

    try:
        proc = subprocess.run(
            [str(KITTEN_PYTHON), "-c", runner_code],
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        err_msg = e.stderr or e.stdout or str(e)
        raise RuntimeError(f"Voiceover synthesis failed:\n{err_msg}")

    if not output_path.is_file() or output_path.stat().st_size == 0:
        raise RuntimeError(f"Voiceover output file was not generated: {output_path}")

    duration = get_audio_duration(output_path)
    print(f"  ✅ Voiceover Generated: {duration:.2f}s -> {output_path.name}\n")

    return {
        "audio_file": output_path.resolve(),
        "duration": duration,
        "text": text
    }
