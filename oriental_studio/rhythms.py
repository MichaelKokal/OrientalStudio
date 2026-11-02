"""Arabic rhythm patterns.

Each pattern is one bar of 4 beats written on a 16th-note grid,
so every beat is 4 characters long:

    D = dum (low, deep hit in the middle of the drum)
    T = tak (high, sharp hit on the rim)
    K = ka  (softer rim hit, usually with the other hand)
    . = rest

Edit these or add your own - the engine picks them up automatically.
"""

STEPS_PER_BEAT = 4

RHYTHMS = {
    #            beat 1   beat 2   beat 3   beat 4
    "maqsoum": "D.T." "..T." "D..." "T...",
    "baladi":  "D.D." "..T." "D..." "T...",
    "saidi":   "D.T." "..D." "D..." "T...",
    "malfuf":  "D..T" "..T." "D..T" "..T.",
    "ayoub":   "D..K" "D.T." "D..K" "D.T.",
    "dabke":   "D.TK" "D.T." "D.TK" "D.T.",
}


def get_pattern(name, fill=False):
    """Return the pattern string for a rhythm.

    With fill=True, empty 8th notes get a soft ka so the groove
    sounds fuller, the way a real darbuka player would play it.
    """
    pattern = RHYTHMS[name]
    if not fill:
        return pattern
    return "".join(
        "K" if ch == "." and i % 2 == 0 else ch
        for i, ch in enumerate(pattern)
    )


def beats_per_bar(pattern):
    return len(pattern) // STEPS_PER_BEAT
