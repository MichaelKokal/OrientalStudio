"""Placing drum hits on a song's beats and mixing everything together."""

import numpy as np

from .drums import kit
from .rhythms import STEPS_PER_BEAT, beats_per_bar


def render_drums(pattern, beats, sr, length, first_beat=0):
    """Play the rhythm pattern along the song's real beat times.

    Each gap between two beats is split into 16th notes, so if the
    song speeds up or slows down the drums follow it.
    """
    sounds = kit(sr)
    per_bar = beats_per_bar(pattern)
    out = np.zeros(length)

    for i, start in enumerate(beats):
        if i + 1 < len(beats):
            gap = beats[i + 1] - start
        elif i > 0:
            gap = start - beats[i - 1]
        else:
            break

        beat_in_bar = (i - first_beat) % per_bar
        for step in range(STEPS_PER_BEAT):
            hit = pattern[beat_in_bar * STEPS_PER_BEAT + step]
            if hit == ".":
                continue
            pos = int((start + gap * step / STEPS_PER_BEAT) * sr)
            sound = sounds[hit][: max(0, length - pos)]
            out[pos:pos + len(sound)] += sound
    return out


def mix(song, drums, song_volume=1.0, drum_volume=0.8):
    """Put the drums on top of the stereo song and keep it from clipping."""
    mixed = song * song_volume + drums[np.newaxis, :] * drum_volume
    peak = np.abs(mixed).max()
    if peak > 0.99:
        mixed *= 0.99 / peak
    return mixed
