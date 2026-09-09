import os
import hashlib
import torch
import numpy as np
import scipy.io.wavfile as wavfile
import subprocess
import shutil
import re
try:
    from manim_voiceover.services.base import SpeechService
except ImportError:
    class SpeechService:
        def __init__(self, **kwargs):
            self.cache_dir = kwargs.get("cache_dir", ".cache_voiceover")
        def get_cached_result(self, input_data, cache_dir):
            return None

try:
    from qwen_tts import Qwen3TTSModel
except ImportError:
    print("Warning: qwen-tts is not installed. Please install it using `pip install qwen-tts`")

class QwenTTSService(SpeechService):
    """
    Manim Voiceover adapter for Qwen3-TTS.
    Provides native, zero-shot voice cloning using Qwen3-TTS 0.6B Base model.
    Includes built-in sentence chunking to prevent OOM errors.
    """
    
    @staticmethod
    def get_optimal_device() -> str:
        """Dynamically detect available compute hardware: Intel Arc (XPU), NVIDIA (CUDA), or CPU."""
        if hasattr(torch, "xpu") and torch.xpu.is_available():
            dev_name = torch.xpu.get_device_name(0) if hasattr(torch.xpu, "get_device_name") else "Intel Arc GPU"
            print(f"[QwenTTSService] Detected Intel Arc Hardware: {dev_name} (using 'xpu')")
            return "xpu"
        if torch.cuda.is_available():
            dev_name = torch.cuda.get_device_name(0) if hasattr(torch.cuda, "get_device_name") else "NVIDIA GPU"
            print(f"[QwenTTSService] Detected NVIDIA Hardware: {dev_name} (using 'cuda:0')")
            return "cuda:0"
        print("[QwenTTSService] No discrete GPU detected, falling back to CPU")
        return "cpu"

    @staticmethod
    def empty_device_cache():
        """Safely clear VRAM cache across XPU, CUDA, or CPU."""
        if hasattr(torch, "xpu") and torch.xpu.is_available():
            torch.xpu.empty_cache()
        elif torch.cuda.is_available():
            torch.cuda.empty_cache()

    def __init__(self, reference_audio: str = "assets/tee_voice_16k.wav", speed: float = 1.35, **kwargs):
        super().__init__(**kwargs)

        # Resolve path relative to script location or project root
        if not os.path.isabs(reference_audio):
            # Try to resolve from project root (assumes we're in science_vids/)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            absolute_path = os.path.join(project_root, reference_audio)

            if os.path.exists(absolute_path):
                self.reference_audio = absolute_path
            else:
                # Fallback to relative path
                self.reference_audio = reference_audio
        else:
            self.reference_audio = reference_audio

        self.speed = speed

        # We need an accurate reference transcript for Qwen3-TTS zero-shot cloning
        self.reference_text = "Plostidium Modulinum is generally diverse, gram-positive, spoof forming, obligate and row."

        if not os.path.exists(self.reference_audio):
            raise FileNotFoundError(f"Reference audio not found: {self.reference_audio}. Please ensure assets/tee_voice_16k.wav exists in the project root.")
            
        self.device = self.get_optimal_device()
        print(f"[QwenTTSService] Loading Qwen3-TTS 0.6B Base Model into {self.device.upper()}...")
        try:
            dtype = torch.bfloat16 if self.device != "cpu" else torch.float32
            self.model = Qwen3TTSModel.from_pretrained(
                "Qwen/Qwen3-TTS-12Hz-0.6B-Base",
                device_map=self.device,
                dtype=dtype,
            )
            print(f"[QwenTTSService] Ready to clone on {self.device.upper()}!")
        except Exception as e:
            print(f"[QwenTTSService] Failed to load model: {e}")

    def chunk_text(self, text: str):
        """Splits text into sentences for batch processing to avoid OOM."""
        # Split on standard sentence delimiters
        sentences = re.split(r'(?<=[.!?]) +', text)
        return [s.strip() for s in sentences if s.strip()]

    def generate_from_text(self, text: str, cache_dir: str = None, path: str = None) -> dict:
        if cache_dir is None:
            cache_dir = self.cache_dir

        input_data = {
            "input_text": text,
            "service": "qwen3-tts",
            "reference_audio": self.reference_audio,
            "speed": self.speed
        }

        cached_result = self.get_cached_result(input_data, cache_dir)
        if cached_result is not None:
            return cached_result

        if path is None:
            audio_hash = hashlib.sha256(str(input_data).encode('utf-8')).hexdigest()[:12]
            audio_path = audio_hash + ".wav"
            file_path = os.path.join(cache_dir, audio_path)
        else:
            file_path = path
            audio_path = os.path.basename(file_path)

        print(f"[QwenTTSService] Generating chunked audio for: '{text}'")
        sentences = self.chunk_text(text)
        
        all_wavs = []
        sample_rate = None
        
        for idx, sentence in enumerate(sentences):
            # Qwen generation
            wavs, sr = self.model.generate_voice_clone(
                text=sentence,
                language="English",
                ref_audio=self.reference_audio,
                ref_text=self.reference_text,
            )
            sample_rate = sr
            all_wavs.append(wavs[0])
            # Clear cache to prevent cumulative OOM
            self.empty_device_cache()
            
        final_audio = np.concatenate(all_wavs)
        
        # Qwen output is usually float32 [-1, 1], convert to int16 for wavfile
        audio_int16 = np.clip(final_audio * 32767, -32768, 32767).astype(np.int16)
        wavfile.write(file_path, sample_rate, audio_int16)

        # Apply Radio/Podcast EQ and Compression using ffmpeg
        tmp_path = file_path + ".tmp.wav"
        filter_chain = (
            "highpass=f=80,lowpass=f=14000,"
            "equalizer=f=120:width_type=h:width=50:g=3,"
            "equalizer=f=4000:width_type=h:width=200:g=2,"
            "acompressor=threshold=-16dB:ratio=4:attack=5:release=50:makeup=4,"
            "loudnorm=I=-16:TP=-1.5:LRA=11"
        )
        if getattr(self, "speed", 1.0) != 1.0:
            filter_chain += f",atempo={self.speed}"
        try:
            subprocess.run([
                "ffmpeg", "-y", "-i", file_path, 
                "-af", filter_chain,
                "-ar", str(sample_rate), "-ac", "1",
                tmp_path
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            shutil.move(tmp_path, file_path)
            print(f"[QwenTTSService] Applied Radio/Podcast EQ to: {audio_path}")
        except subprocess.CalledProcessError as e:
            print(f"[QwenTTSService] Warning: Could not apply EQ via ffmpeg. {e}")
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

        json_dict = {
            "input_text": text,
            "input_data": input_data,
            "original_audio": audio_path,
        }

        return json_dict
