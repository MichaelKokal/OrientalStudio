"""Plays rhythms live, with a tempo you can change while it plays.

The sound card asks for audio a few milliseconds at a time, and we work out
exactly which sample each drum hit lands on. That keeps the beat steady no
matter what the rest of the program is doing.
"""

import numpy as np
import sounddevice as sd

from .rhythms import STEPS_PER_BEAT, beats_per_bar, get_pattern

SAMPLE_RATE = 48000


class RhythmPlayer:
    def __init__(self, kits, rhythm="maqsoum", bpm=100):
        self.kits = kits                    # kit name -> {"D": audio, "T": audio, "K": audio}
        self.kit = next(iter(kits))
        self.bpm = bpm
        self.volume = 0.8
        self.playing = False
        self.rhythm = rhythm
        self.fill = False
        self._pattern = get_pattern(rhythm)
        self._next_pattern = None           # waits for the end of the bar
        self._step = 0
        self._samples_to_step = 0.0
        longest = max(len(s) for k in kits.values() for s in k.values())
        self._ring = np.zeros(longest + 4096)   # hits still ringing out
        self.stream = sd.OutputStream(samplerate=SAMPLE_RATE, channels=2, blocksize=256,
                                      latency="low", callback=self._callback)
        self.stream.start()

    def set_rhythm(self, rhythm=None, fill=None):
        """Switch rhythm or fill. While playing, it changes at the start of the next bar."""
        self.rhythm = rhythm or self.rhythm
        self.fill = self.fill if fill is None else fill
        pattern = get_pattern(self.rhythm, self.fill)
        if self.playing:
            self._next_pattern = pattern
        else:
            self._pattern = pattern

    def start(self):
        self._step = 0
        self._samples_to_step = 0.0
        if self._next_pattern:
            self._pattern, self._next_pattern = self._next_pattern, None
        self.playing = True

    def stop(self):
        self.playing = False

    @property
    def beat(self):
        """Which beat of the bar is playing (0 = beat 1)."""
        return (self._step - 1) % len(self._pattern) // STEPS_PER_BEAT

    @property
    def beats_in_bar(self):
        return beats_per_bar(self._pattern)

    def _callback(self, outdata, frames, time, status):
        if self.playing:
            step_length = SAMPLE_RATE * 60 / self.bpm / STEPS_PER_BEAT
            sounds = self.kits[self.kit]
            while self._samples_to_step < frames:
                if self._step == 0 and self._next_pattern:
                    self._pattern, self._next_pattern = self._next_pattern, None
                hit = self._pattern[self._step]
                if hit != ".":
                    at = int(self._samples_to_step)
                    sound = sounds[hit][: len(self._ring) - at]
                    self._ring[at:at + len(sound)] += sound
                self._step = (self._step + 1) % len(self._pattern)
                self._samples_to_step += step_length
            self._samples_to_step -= frames

        block = self._ring[:frames] * self.volume
        outdata[:] = np.clip(block, -1, 1)[:, np.newaxis]
        self._ring[:-frames] = self._ring[frames:]
        self._ring[-frames:] = 0

    def close(self):
        self.stream.stop()
        self.stream.close()
