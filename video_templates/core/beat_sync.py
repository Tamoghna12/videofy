"""
beat_sync.py - AI Beat-Drop & Musical Transient Synchronization Engine.
Extracts musical rhythm downbeats, energy onsets, and tempo transients to snap
timeline video cuts and Polaroid shutter flashes directly to the music.
"""

import subprocess
from pathlib import Path
import numpy as np
import scipy.signal


def extract_audio_samples(audio_path, duration=None, sr=22050):
    """Extract raw mono audio samples as a normalized float numpy array using FFmpeg."""
    cmd = ["ffmpeg", "-v", "error"]
    if duration:
        cmd.extend(["-t", f"{duration:.2f}"])
    cmd.extend([
        "-i", str(audio_path),
        "-f", "s16le",
        "-ac", "1",
        "-ar", str(sr),
        "-"
    ])
    try:
        raw = subprocess.check_output(cmd)
        samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        return samples, sr
    except Exception as e:
        raise RuntimeError(f"Failed to decode audio samples from {audio_path}: {e}")


def detect_beats(audio_path, duration=None, min_interval=0.5):
    """
    Detects musical downbeats and energy transient peaks from an audio file.
    Returns:
      {
        "beats": [t0, t1, t2, ...],
        "tempo_estimate_bpm": float,
        "sample_rate": int
      }
    """
    # 1. First attempt librosa if available without dependency mismatch
    try:
        import librosa
        y, sr = librosa.load(str(audio_path), sr=22050, duration=duration)
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        beat_times = librosa.frames_to_time(beat_frames, sr=sr).tolist()
        if len(beat_times) >= 3:
            return {
                "beats": [float(b) for b in beat_times],
                "tempo_estimate_bpm": float(tempo),
                "engine": "librosa"
            }
    except Exception:
        # Fall through to high-performance Scipy transient detector
        pass

    # 2. High-performance Scipy spectral & energy transient onset detector
    samples, sr = extract_audio_samples(audio_path, duration=duration, sr=22050)
    if len(samples) < sr:
        return {"beats": [], "tempo_estimate_bpm": 120.0, "engine": "fallback"}

    # Focus on rhythm & bass transients (kick, snare, drops: 30Hz - 250Hz bandpass)
    sos = scipy.signal.butter(4, [30, 250], btype="bandpass", fs=sr, output="sos")
    filtered = scipy.signal.sosfilt(sos, samples)

    # Compute short-time RMS energy envelope
    hop_size = 512
    frames = len(filtered) // hop_size
    envelope = np.array([
        np.sqrt(np.mean(filtered[i * hop_size : (i + 1) * hop_size] ** 2) + 1e-8)
        for i in range(frames)
    ])

    # Normalize envelope
    max_val = np.max(envelope)
    if max_val > 0:
        envelope /= max_val

    # Distance constraint based on min_interval (default 0.5s = max 120 cuts/min)
    min_dist_frames = max(1, int(min_interval * sr / hop_size))
    peaks, properties = scipy.signal.find_peaks(
        envelope,
        height=0.20,
        distance=min_dist_frames,
        prominence=0.10
    )

    beat_times = (peaks * hop_size / float(sr)).tolist()

    # Estimate average tempo (BPM) from inter-beat intervals
    if len(beat_times) >= 2:
        diffs = np.diff(beat_times)
        valid_diffs = diffs[(diffs >= 0.25) & (diffs <= 1.5)]
        if len(valid_diffs) > 0:
            median_interval = np.median(valid_diffs)
            bpm = round(60.0 / median_interval, 1)
        else:
            bpm = 120.0
    else:
        bpm = 120.0

    return {
        "beats": [round(float(b), 3) for b in beat_times],
        "tempo_estimate_bpm": bpm,
        "engine": "scipy_transient"
    }


def snap_timeline_to_beats(requested_durations, beats, tolerance=0.85):
    """
    Snaps a sequence of requested segment durations to musical beat drops.
    
    Arguments:
      requested_durations: list of float durations (e.g. [4.5, 2.4, 4.5, 2.4])
      beats: list of detected beat timestamps (in seconds)
      tolerance: maximum shift in seconds to snap to a beat
      
    Returns:
      snapped_durations: list of adjusted durations
      cut_timestamps: exact transition timestamps aligned with music
    """
    if not beats or len(beats) == 0:
        # No beats to snap to, return requested as-is
        cuts = []
        curr = 0.0
        for d in requested_durations:
            curr += d
            cuts.append(curr)
        return requested_durations, cuts

    snapped_durations = []
    cut_timestamps = []
    curr_time = 0.0

    for i, req_dur in enumerate(requested_durations):
        target_cut = curr_time + req_dur
        
        # Don't snap the very last cut to allow audio fade-out
        if i == len(requested_durations) - 1:
            snapped_durations.append(round(req_dur, 2))
            cut_timestamps.append(round(curr_time + req_dur, 2))
            break

        # Find closest beat to target_cut
        candidate_beats = [b for b in beats if abs(b - target_cut) <= tolerance and b > curr_time + 1.2]
        if candidate_beats:
            best_beat = min(candidate_beats, key=lambda b: abs(b - target_cut))
            actual_dur = max(1.2, best_beat - curr_time)
        else:
            actual_dur = req_dur

        snapped_durations.append(round(actual_dur, 2))
        curr_time += actual_dur
        cut_timestamps.append(round(curr_time, 2))

    return snapped_durations, cut_timestamps
