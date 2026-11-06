"""Using the computer keyboard as a piano until the Casio is connected.

      W E   T Y U   O P          <- black keys
     A S D F G H J K L ; '       <- white keys, starting on C
"""

WHITE_KEYS = ["a", "s", "d", "f", "g", "h", "j", "k", "l", "semicolon", "apostrophe"]
WHITE_STEPS = [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17]
BLACK_KEYS = {"w": 1, "e": 3, "t": 6, "y": 8, "u": 10, "o": 13, "p": 15}

# Computer key -> how many semitones above the starting C
KEY_STEPS = {**dict(zip(WHITE_KEYS, WHITE_STEPS)), **BLACK_KEYS}
LABELS = {"semicolon": ";", "apostrophe": "'"}

NOTE_NAMES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]


def note_name(note, quarter_flat=False):
    """60 -> 'C4', and 64 with quarter_flat -> 'E4 half-flat'"""
    name = f"{NOTE_NAMES[note % 12]}{note // 12 - 1}"
    return name + " half-flat" if quarter_flat else name


def label(key):
    return LABELS.get(key, key.upper())
