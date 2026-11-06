# Oriental Studio

Turning a Casio CTK-574 into an Arabic / Oriental keyboard using Python, MIDI and free software.

## What works so far

**Play instruments live.** A window with 9 instruments (piano, oud, qanun, buzuq, ney, mijwiz, violin, strings, accordion) and an on-screen piano. Until the Casio is connected, the computer keyboard is the piano.

**Play in any maqam, with real quarter tones.** Pick Bayati, Rast, Saba, Sikah, Huzam, Hijaz, Nahawand, Kurd or Ajam and the right keys are retuned. In Bayati on D, the E key plays E half-flat, which a normal piano can't do. Move the root and the quarter tones move with it. Dots on the piano show which keys belong to the maqam.

**Add Arabic rhythms to any song.** Load an MP3 or WAV, and Oriental Studio finds the beat and plays a darbuka rhythm in time with it. It follows the song's real beats instead of one fixed tempo, so it stays in sync with live recordings that speed up and slow down.

Rhythms: maqsoum, baladi, saidi, malfuf, ayoub, dabke.

## Setup (Windows)

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python setup_sounds.py
```

`setup_sounds.py` downloads the free [FluidSynth](https://www.fluidsynth.org/) sound engine and the [GeneralUser GS](https://github.com/mrbumpy409/GeneralUser-GS) sound bank (about 35 MB).

## Play instruments

```
python play.py
```

```
   W E   T Y U   O P          black keys
  A S D F G H J K L ; '       white keys (A = C)
  Z / X                       octave down / up
  1 - 9                       pick an instrument
  Up / Down                   pick a maqam
  Left / Right                move the maqam's root
```

You can also click the keys and buttons on screen. Maqamat live in `oriental_studio/maqamat.py`, and quarter tones are set to exactly half a semitone there (`QUARTER_FLAT = -50`) if you want to tune them by ear.

The free sound bank has no real Arabic instruments yet, so oud, qanun, buzuq, ney and mijwiz use the closest sounds it has (nylon guitar, harp, sitar, shakuhachi and shenai). Real recordings come later.

## Add rhythms to a song

```
python studio.py --list                                   # show rhythms
python studio.py songs/song.mp3 --rhythm maqsoum          # play it
python studio.py songs/song.mp3 --rhythm dabke --fill     # fuller groove
python studio.py songs/song.mp3 --rhythm saidi --out mix.wav
```

If the drums don't line up:

| Problem | Fix |
|---|---|
| Drums too fast | `--half` |
| Drums too slow | `--double` |
| Pattern starts on the wrong beat | `--shift 1` (or 2, 3) |
| Tempo totally off | `--bpm 95` (rough guess is fine) |

Rhythm patterns live in `oriental_studio/rhythms.py` as simple text (`D` = dum, `T` = tak, `K` = ka, `.` = rest), so they're easy to edit.

## Roadmap

1. Song import + beat sync ✅
2. Instrument sounds, played from the computer keyboard ✅
3. Maqamat with quarter tones ✅
4. Connect the Casio over USB-MIDI
5. Live rhythm engine with tempo control
6. Real Arabic instrument and darbuka recordings
7. Automatic accompaniment (bass, chords, drums from left-hand chords)
8. Full performance interface
