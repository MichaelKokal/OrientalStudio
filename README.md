# Oriental Studio

Turning a Casio CTK-574 into an Arabic / Oriental keyboard using Python, MIDI and free software.

## What works so far

**Add Arabic rhythms to any song.** Load an MP3 or WAV, and Oriental Studio finds the beat and plays a darbuka rhythm in time with it. It follows the song's real beats instead of one fixed tempo, so it stays in sync with live recordings that speed up and slow down.

Rhythms: maqsoum, baladi, saidi, malfuf, ayoub, dabke.

## Setup (Windows)

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

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
2. Connect the Casio over USB-MIDI and play sounds from the computer
3. Arabic instruments: oud, qanun, mijwiz, ney
4. Maqamat with quarter tones
5. Automatic accompaniment (bass, chords, drums from left-hand chords)
6. Full performance interface
