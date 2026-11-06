"""Maqamat: Arabic scales, including the quarter tones a piano can't play.

Each maqam lists its notes as semitones above the root, and which of those
notes are lowered by a quarter tone. You play the normal key (E in Bayati
on D) and it sounds a quarter tone flat, the way Oriental arranger
keyboards do it. Changing the root moves the quarter tones with it.
"""

from dataclasses import dataclass

# How far a quarter-flat note is lowered, in cents (100 cents = 1 semitone).
# Exactly half a semitone is the textbook value; players often tune it by ear.
QUARTER_FLAT = -50


@dataclass(frozen=True)
class Maqam:
    name: str
    root: int                 # usual starting note (0 = C, 2 = D, 4 = E ...)
    notes: tuple = ()         # semitones above the root
    quarter_flat: tuple = ()  # which of those notes are a quarter tone flat


MAQAMAT = [
    Maqam("Off", 0),
    Maqam("Bayati", 2, (0, 2, 3, 5, 7, 8, 10), (2,)),
    Maqam("Rast", 0, (0, 2, 4, 5, 7, 9, 11), (4, 11)),
    Maqam("Saba", 2, (0, 2, 3, 4, 7, 8, 10), (2,)),
    Maqam("Sikah", 4, (0, 1, 3, 5, 7, 8, 10), (0, 7)),
    Maqam("Huzam", 4, (0, 1, 3, 4, 7, 8, 10), (0,)),
    Maqam("Hijaz", 2, (0, 1, 4, 5, 7, 8, 10)),
    Maqam("Nahawand", 0, (0, 2, 3, 5, 7, 8, 11)),
    Maqam("Kurd", 2, (0, 1, 3, 5, 7, 8, 10)),
    Maqam("Ajam", 0, (0, 2, 4, 5, 7, 9, 11)),
]


def offsets(maqam, root):
    """How many cents to shift each of the 12 notes (index 0 = C)."""
    shift = [0.0] * 12
    for step in maqam.quarter_flat:
        shift[(root + step) % 12] = QUARTER_FLAT
    return shift


def scale_notes(maqam, root):
    """The notes (0-11) that belong to the maqam starting on this root."""
    return {(root + step) % 12 for step in maqam.notes}
