"""The sound engine: turns notes into instrument sounds with FluidSynth."""

import os
from pathlib import Path

ROOT = Path(__file__).parent.parent
SOUNDFONT = ROOT / "soundfonts" / "GeneralUser-GS.sf2"


def _find_fluidsynth():
    """Let Python find the FluidSynth library that setup_sounds.py downloaded."""
    for dll in (ROOT / "third_party").glob("**/libfluidsynth*.dll"):
        os.add_dll_directory(str(dll.parent))
        os.environ["PATH"] = str(dll.parent) + os.pathsep + os.environ["PATH"]
        return
    raise SystemExit("FluidSynth not found. Run: python setup_sounds.py")


_find_fluidsynth()
import fluidsynth  # noqa: E402  (needs the library path set up first)


class Synth:
    def __init__(self, soundfont=SOUNDFONT):
        if not Path(soundfont).exists():
            raise SystemExit("Sounds not found. Run: python setup_sounds.py")
        # Small audio buffers keep the delay between key press and sound short.
        # 48000 matches most Windows sound cards, so nothing gets resampled.
        self.fs = fluidsynth.Synth(gain=0.6, samplerate=48000)
        self.fs.setting("audio.period-size", 256)
        self.fs.setting("audio.periods", 2)
        self.fs.setting("audio.driver", "wasapi")
        # Start only the audio output. Synth.start() would also open every MIDI
        # input, and Windows lets just one program use a MIDI port at a time,
        # so it would lock out the Casio.
        self.fs.audio_driver = fluidsynth.new_fluid_audio_driver(self.fs.settings, self.fs.synth)
        self.fs.midi_driver = None
        self.sfid = self.fs.sfload(str(soundfont))
        self.channel = 0

    def set_instrument(self, bank, preset):
        self.fs.program_select(self.channel, self.sfid, bank, preset)

    def note_on(self, note, velocity=100):
        self.fs.noteon(self.channel, note, velocity)

    def note_off(self, note):
        self.fs.noteoff(self.channel, note)

    def all_notes_off(self):
        self.fs.all_notes_off(self.channel)

    def preset_name(self, bank, preset):
        return self.fs.sfpreset_name(self.sfid, bank, preset)

    def close(self):
        self.fs.delete()
