"""Loading songs and finding their beats."""

import librosa
import numpy as np

SAMPLE_RATE = 44100


def load(path):
    """Load an MP3/WAV/FLAC as stereo audio. Returns (audio, sample_rate)."""
    audio, sr = librosa.load(path, sr=SAMPLE_RATE, mono=False)
    if audio.ndim == 1:
        audio = np.stack([audio, audio])
    return audio, sr


def find_beats(audio, sr, tempo_hint=None):
    """Find where every beat lands in the song.

    We keep the real beat times instead of assuming one fixed tempo,
    because live recordings speed up and slow down.
    Returns (average_bpm, beat_times_in_seconds, onset_strength).
    """
    mono = librosa.to_mono(audio)
    onset = librosa.onset.onset_strength(y=mono, sr=sr)
    tempo, beats = librosa.beat.beat_track(
        onset_envelope=onset, sr=sr, units="time",
        start_bpm=tempo_hint or 120,
    )
    return float(np.atleast_1d(tempo)[0]), beats, onset


def guess_first_beat(beats, onset, sr, beats_per_bar):
    """Guess which beat is "beat 1" of the bar.

    Beat 1 is usually the strongest, so we try each starting position
    and keep the one whose beats are loudest on average.
    """
    frames = librosa.time_to_frames(beats, sr=sr)
    strength = onset[np.clip(frames, 0, len(onset) - 1)]
    scores = [strength[start::beats_per_bar].mean() for start in range(beats_per_bar)]
    return int(np.argmax(scores))


def double_time(beats):
    """Add a beat halfway between each pair (when detection found half the beats)."""
    middles = (beats[:-1] + beats[1:]) / 2
    return np.sort(np.concatenate([beats, middles]))


def half_time(beats):
    """Keep every other beat (when detection found twice as many beats)."""
    return beats[::2]
