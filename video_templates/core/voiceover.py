"""
voiceover.py - AI Zero-Shot Cloned Voiceover & Kinetic Highlighted Subtitle Engine
Bridges Videofy with the local Qwen3-TTS 0.6B GPU service in the 'kitten'
environment to synthesize personalized narration with word-by-word highlighted
kinetic subtitles and spaced narrative timing across the video timeline.
"""

import os
import sys
import re
import json
import subprocess
import tempfile
import numpy as np
import scipy.io.wavfile as wavfile
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_REF_AUDIO = WORKSPACE_ROOT / "assets" / "audio" / "voice" / "tee_voice_16k.wav"


def get_voiceover_python() -> Path:
    """Resolve the python interpreter capable of running Qwen-TTS and faster-whisper."""
    env_py = os.environ.get("VOICEOVER_PYTHON")
    if env_py and Path(env_py).is_file():
        return Path(env_py)
    candidates = [
        Path.home() / "anaconda3/envs/kitten/bin/python",
        Path.home() / "miniconda3/envs/kitten/bin/python",
        Path("/home/tamoghna/anaconda3/envs/kitten/bin/python"),
        Path(sys.executable),
    ]
    for cand in candidates:
        if cand.is_file():
            return cand
    return Path(sys.executable)


def is_voiceover_available() -> bool:
    """Check if the local voice cloning environment and voice sample are available."""
    py = get_voiceover_python()
    return py.is_file() and DEFAULT_REF_AUDIO.is_file()


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


def format_ass_time(seconds: float) -> str:
    """Format seconds into ASS timestamp string: H:MM:SS.cs"""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = seconds % 60
    centis = int((secs - int(secs)) * 100)
    return f"{hrs}:{mins:02d}:{int(secs):02d}.{centis:02d}"


def parse_narration_phrases(text: str) -> list[str]:
    """
    Parse a narration script into spaced narrative phrases.
    Supports delimiter '|', double newlines, or sentence boundaries.
    """
    if " | " in text:
        parts = [p.strip() for p in text.split(" | ") if p.strip()]
    elif "\n\n" in text:
        parts = [p.strip() for p in text.split("\n\n") if p.strip()]
    elif "\n" in text:
        parts = [p.strip() for p in text.split("\n") if p.strip()]
    else:
        # Split on sentence terminals if multi-sentence
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        if len(sentences) > 3:
            # Group into 3 balanced parts
            k, m = divmod(len(sentences), 3)
            parts = [
                " ".join(sentences[i*k + min(i, m):(i+1)*k + min(i+1, m)])
                for i in range(3)
            ]
        else:
            parts = sentences

    return [p for p in parts if p]


def generate_spaced_story_voiceover(
    narration: str,
    total_duration: float,
    output_dir: Path,
    speed: float = 0.92,
    reference_audio: Path = None,
    font_size: int = 50,
    margin_v: int = 360,
    play_res_x: int = 1080,
    play_res_y: int = 1920,
    margin_lr: int = 80
) -> dict:
    """
    Synthesizes spaced, contemplative storytelling voiceover across the video duration
    and produces word-level kinetic highlighted ASS subtitles.
    
    Args:
        narration: Narration script (use ' | ' to explicitly divide phrases).
        total_duration: Target timeline duration in seconds.
        output_dir: Folder to write generated audio and ASS subtitle file.
        speed: Speech tempo factor (default: 0.92 for slow, unhurried, reflective delivery).
        reference_audio: Cloned voice reference sample.
        font_size: ASS subtitle font size.
        
    Returns:
        dict: {
            "audio_file": Path (full-duration WAV with spaced voiceover),
            "subtitles_ass": Path (kinetic word-highlight ASS file),
            "ducking_intervals": list[tuple[float, float]],
            "phrases": list[dict]
        }
    """
    py_bin = get_voiceover_python()
    if not is_voiceover_available():
        raise RuntimeError(f"Voiceover environment not ready: {py_bin}")

    ref_audio = Path(reference_audio) if reference_audio else DEFAULT_REF_AUDIO
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    phrases = parse_narration_phrases(narration)
    num_phrases = len(phrases)
    if num_phrases == 0:
        return None

    print(f"\n🎙️ Synthesizing Spaced Story Voiceover ({num_phrases} phrases across {total_duration:.1f}s)...")

    # 1. Execute synthesis and Whisper word extraction in kitten conda environment
    tmp_json_req = output_dir / "_voiceover_req.json"
    tmp_json_res = output_dir / "_voiceover_res.json"

    req_payload = {
        "phrases": phrases,
        "ref_audio": str(ref_audio),
        "speed": float(speed),
        "out_dir": str(output_dir)
    }
    tmp_json_req.write_text(json.dumps(req_payload), encoding="utf-8")

    runner_code = f"""
import sys, os, json
sys.path.append({json.dumps(str(WORKSPACE_ROOT))})
from video_templates.core.qwen_tts_service import QwenTTSService
from faster_whisper import WhisperModel

with open({json.dumps(str(tmp_json_req))}) as f:
    req = json.load(f)

import torch
service = QwenTTSService(reference_audio=req['ref_audio'], speed=req['speed'])
w_dev = 'cuda' if torch.cuda.is_available() else 'cpu'
w_comp = 'float16' if w_dev == 'cuda' else 'int8'
whisper = WhisperModel('base', device=w_dev, compute_type=w_comp)

results = []
for i, phrase in enumerate(req['phrases']):
    out_wav = os.path.join(req['out_dir'], f"phrase_{{i}}.wav")
    if not (os.path.isfile(out_wav) and os.path.getsize(out_wav) > 10000):
        service.generate_from_text(phrase, path=out_wav)
    
    segments, _ = whisper.transcribe(out_wav, word_timestamps=True, initial_prompt=phrase)
    words = []
    for seg in segments:
        for w in seg.words:
            words.append({{
                "word": w.word.strip(),
                "start": float(w.start),
                "end": float(w.end)
            }})
    
    # Align exact original script words if count matches
    orig_tokens = phrase.split()
    if len(words) == len(orig_tokens):
        for idx in range(len(words)):
            words[idx]["word"] = orig_tokens[idx]
    elif abs(len(words) - len(orig_tokens)) <= 2:
        for idx in range(min(len(words), len(orig_tokens))):
            if words[idx]["word"].lower() == orig_tokens[idx].lower() or orig_tokens[idx].lower().startswith(words[idx]["word"].lower()[:3]):
                words[idx]["word"] = orig_tokens[idx]
    
    # Probe duration
    import subprocess
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", out_wav]
    dur = float(subprocess.check_output(cmd).decode().strip())
    
    results.append({{
        "index": i,
        "text": phrase,
        "wav_file": out_wav,
        "duration": dur,
        "words": words
    }})

with open({json.dumps(str(tmp_json_res))}, "w") as f:
    json.dump(results, f)

print("SPACED_SYNTHESIS_SUCCESS")
"""

    env = os.environ.copy()
    for k in ["CONDA_PREFIX", "CONDA_DEFAULT_ENV", "CONDA_PROMPT_MODIFIER", "PYTHONPATH"]:
        env.pop(k, None)

    py_bin = get_voiceover_python()
    try:
        subprocess.run(
            [str(py_bin), "-c", runner_code],
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        err = e.stderr or e.stdout or str(e)
        raise RuntimeError(f"Spaced voiceover synthesis failed:\n{err}")

    if not tmp_json_res.is_file():
        raise RuntimeError("Synthesis response file was not created.")

    phrase_data = json.loads(tmp_json_res.read_text(encoding="utf-8"))
    tmp_json_req.unlink(missing_ok=True)
    tmp_json_res.unlink(missing_ok=True)

    # 2. Compute Spaced Timeline Start Points
    # Phrase 0: ~2.0s in
    # Even spacing for subsequent phrases leaving pauses for music swells
    if num_phrases == 1:
        start_times = [2.0]
    elif num_phrases == 2:
        start_times = [2.0, max(12.0, total_duration * 0.50)]
    elif num_phrases == 3:
        start_times = [2.0, max(12.0, total_duration * 0.40), max(22.0, total_duration * 0.70)]
    else:
        # Dynamic even spacing
        gap = (total_duration - 7.0) / num_phrases
        start_times = [2.0 + i * gap for i in range(num_phrases)]

    ducking_intervals = []
    sample_rate = 24000
    timeline_audio_samples = int(total_duration * sample_rate)
    full_audio_buffer = np.zeros(timeline_audio_samples, dtype=np.int16)

    for i, item in enumerate(phrase_data):
        t_start = start_times[i]
        dur = item["duration"]
        item["timeline_start"] = t_start
        item["timeline_end"] = t_start + dur
        ducking_intervals.append((max(0.0, t_start - 0.25), min(total_duration, t_start + dur + 0.45)))

        # Load phrase wav and mix into timeline buffer
        sr, audio_data = wavfile.read(item["wav_file"])
        if sr != sample_rate:
            # Resample if needed via simple interpolation
            num_target = int(len(audio_data) * sample_rate / sr)
            audio_data = np.interp(
                np.linspace(0, len(audio_data), num_target, endpoint=False),
                np.arange(len(audio_data)),
                audio_data
            ).astype(np.int16)

        idx_start = int(t_start * sample_rate)
        idx_end = min(len(full_audio_buffer), idx_start + len(audio_data))
        insert_len = idx_end - idx_start
        if insert_len > 0:
            full_audio_buffer[idx_start:idx_end] = np.clip(
                full_audio_buffer[idx_start:idx_end].astype(np.int32) + audio_data[:insert_len].astype(np.int32),
                -32768, 32767
            ).astype(np.int16)

    timeline_wav = output_dir / "timeline_spaced_voiceover.wav"
    wavfile.write(timeline_wav, sample_rate, full_audio_buffer)

    # 3. Generate Kinetic Highlighted ASS Subtitles
    ass_file = output_dir / "kinetic_highlight_subtitles.ass"
    ass_lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {play_res_x}",
        f"PlayResY: {play_res_y}",
        "WrapStyle: 0",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        # Style: Centered lower-third (Alignment=2), bold white with black outline and drop shadow
        f"Style: Default, Liberation Sans, {font_size}, &H00FFFFFF, &H000000FF, &H00000000, &H90000000, 1, 0, 0, 0, 100, 100, 1.2, 0, 1, 3.5, 2.0, 2, {margin_lr}, {margin_lr}, {margin_v}, 1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]

    for item in phrase_data:
        t_base = item["timeline_start"]
        words = item["words"]
        raw_words = [w["word"] for w in words]
        
        if not words:
            # Fallback if no word tokens
            t1_str = format_ass_time(t_base)
            t2_str = format_ass_time(item["timeline_end"])
            ass_lines.append(f"Dialogue: 0,{t1_str},{t2_str},Default,,0,0,0,,{item['text']}")
            continue

        # Optional pre-speech lead-in so the line displays before word 0 begins
        w0_start = t_base + words[0]["start"]
        if w0_start > t_base + 0.08:
            lead_in_text = " ".join([f"{{\\c&H00D0D0D0\\b0}}{w}{{\\r}}" for w in raw_words])
            ass_lines.append(f"Dialogue: 0,{format_ass_time(t_base)},{format_ass_time(w0_start)},Default,,0,0,0,,{lead_in_text}")

        # For each word, emit a dialogue slice highlighting the active word
        for w_idx, w_obj in enumerate(words):
            w_start = t_base + w_obj["start"]
            # Hold highlight until next word starts or end of phrase
            if w_idx + 1 < len(words):
                w_end = t_base + words[w_idx + 1]["start"]
            else:
                w_end = t_base + w_obj["end"] + 0.45

            t1_str = format_ass_time(w_start)
            t2_str = format_ass_time(w_end)

            # Build line text: active word is glowing radiant gold (\\c&H0000D7FF), others are muted silver (\\c&H00D0D0D0)
            highlighted_line = []
            for j, word_str in enumerate(raw_words):
                if j == w_idx:
                    # Radiant Gold, Bold
                    highlighted_line.append(f"{{\\c&H0000D7FF\\b1}}{word_str}{{\\r}}")
                else:
                    highlighted_line.append(f"{{\\c&H00D0D0D0\\b0}}{word_str}{{\\r}}")

            rendered_text = " ".join(highlighted_line)
            ass_lines.append(f"Dialogue: 0,{t1_str},{t2_str},Default,,0,0,0,,{rendered_text}")

    ass_file.write_text("\n".join(ass_lines), encoding="utf-8")
    print(f"  ✅ Spaced Audio Track: {timeline_wav.name}")
    print(f"  ✅ Kinetic Subtitles : {ass_file.name} ({len(ass_lines) - 13} word events)")

    return {
        "audio_file": timeline_wav.resolve(),
        "subtitles_ass": ass_file.resolve(),
        "ducking_intervals": ducking_intervals,
        "phrases": phrase_data
    }


def generate_voiceover(
    text: str,
    output_path: Path,
    speed: float = 1.0,
    reference_audio: Path = None
) -> dict:
    """Synthesize a single voiceover audio clip with zero-shot cloned voice."""
    py_bin = get_voiceover_python()
    if not is_voiceover_available():
        raise RuntimeError(f"Voiceover environment not ready: {py_bin}")
    ref_audio = Path(reference_audio) if reference_audio else DEFAULT_REF_AUDIO
    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    runner_code = f"""
import sys, os
sys.path.append({json.dumps(str(WORKSPACE_ROOT))})
from video_templates.core.qwen_tts_service import QwenTTSService
service = QwenTTSService(reference_audio={json.dumps(str(ref_audio))}, speed={float(speed)})
service.generate_from_text({json.dumps(text)}, path={json.dumps(str(output_path))})
"""
    env = os.environ.copy()
    for k in ["CONDA_PREFIX", "CONDA_DEFAULT_ENV", "CONDA_PROMPT_MODIFIER", "PYTHONPATH"]:
        env.pop(k, None)

    subprocess.run(
        [str(py_bin), "-c", runner_code],
        env=env,
        capture_output=True,
        text=True,
        check=True
    )
    dur = get_audio_duration(output_path)
    return {
        "audio_file": output_path,
        "duration": dur,
        "text": text
    }

