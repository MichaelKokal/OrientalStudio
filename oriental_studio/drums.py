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


# Hand drums from the sound bank's standard kit, standing in for a darbuka.
CONGA_NOTES = {"D": 64, "T": 60, "K": 62}   # low conga, high bongo, muted high conga


def sound_bank_kit():
    """Real recorded congas and bongos at 48000 Hz, recorded once from the sound bank."""
    from .synth import Synth
    synth = Synth(audio=False)
    hits = {hit: synth.render_drum(note) for hit, note in CONGA_NOTES.items()}
    synth.close()
    hits["K"] *= 0.6
    return hits


def evened(kit, peak=0.7):
    """Scale a kit so its loudest hit reaches `peak`, keeping the hits' balance."""
    loudest = max(np.abs(s).max() for s in kit.values())
    return {hit: s * (peak / loudest) for hit, s in kit.items()}
