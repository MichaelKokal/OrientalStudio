"""Darbuka sounds built from scratch with math, so no sample files are needed.

These are placeholders until we load real darbuka recordings.
"""

import numpy as np


def _time(sr, seconds):
    return np.arange(int(sr * seconds)) / sr


def dum(sr):
    """Deep hit: a low tone that drops in pitch, plus a tiny click."""
    t = _time(sr, 0.45)
    freq = 75 + 70 * np.exp(-t / 0.03)
    body = np.sin(2 * np.pi * np.cumsum(freq) / sr) * np.exp(-t / 0.16)
    noise = np.random.default_rng(1).standard_normal(len(t))
    click = noise * np.exp(-t / 0.004) * 0.25
    return 0.9 * (body + click)


def tak(sr, pitch=1.0, seed=2):
    """Sharp rim hit: a couple of bright tones plus a burst of noise."""
    t = _time(sr, 0.15)
    tone = (np.sin(2 * np.pi * 820 * pitch * t) * np.exp(-t / 0.03)
            + 0.5 * np.sin(2 * np.pi * 1650 * pitch * t) * np.exp(-t / 0.02))
    noise = np.random.default_rng(seed).standard_normal(len(t))
    noise = np.diff(noise, prepend=0) * np.exp(-t / 0.012)
    return 0.45 * tone + 0.3 * noise


def ka(sr):
    """Softer rim hit."""
    return 0.5 * tak(sr, pitch=1.08, seed=3)


def kit(sr):
    return {"D": dum(sr), "T": tak(sr), "K": ka(sr)}
