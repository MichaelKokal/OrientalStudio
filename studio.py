"""Oriental Studio - add Arabic rhythms to any song.

Examples:
    python studio.py --list
    python studio.py songs/my_song.mp3 --rhythm maqsoum
    python studio.py songs/my_song.mp3 --rhythm dabke --fill --out mix.wav
"""

import argparse
import sys

import sounddevice as sd
import soundfile as sf

from oriental_studio import mixer, song
from oriental_studio.rhythms import RHYTHMS, beats_per_bar, get_pattern


def parse_args():
    p = argparse.ArgumentParser(description="Add Arabic rhythms to a song.")
    p.add_argument("song", nargs="?", help="path to an MP3, WAV or FLAC file")
    p.add_argument("--list", action="store_true", help="show available rhythms")
    p.add_argument("--rhythm", default="maqsoum", choices=sorted(RHYTHMS))
    p.add_argument("--fill", action="store_true", help="add soft ka hits in the gaps")
    p.add_argument("--bpm", type=float, help="rough tempo hint if detection is off")
    p.add_argument("--double", action="store_true", help="drums twice as fast")
    p.add_argument("--half", action="store_true", help="drums half as fast")
    p.add_argument("--shift", type=int, help="move beat 1 by this many beats")
    p.add_argument("--song-volume", type=float, default=1.0)
    p.add_argument("--drum-volume", type=float, default=0.8)
    p.add_argument("--drums-only", action="store_true", help="leave the song out")
    p.add_argument("--out", help="save the result to a WAV file instead of playing it")
    return p.parse_args()


def main():
    args = parse_args()

    if args.list:
        for name, pattern in RHYTHMS.items():
            bars = " | ".join(pattern[i:i + 4] for i in range(0, len(pattern), 4))
            print(f"  {name:<8} {bars}")
        return
    if not args.song:
        sys.exit("Give me a song file, or use --list to see rhythms.")

    print(f"Loading {args.song} ...")
    audio, sr = song.load(args.song)

    print("Finding the beat ...")
    bpm, beats, onset = song.find_beats(audio, sr, args.bpm)
    if args.double:
        beats, bpm = song.double_time(beats), bpm * 2
    if args.half:
        beats, bpm = song.half_time(beats), bpm / 2
    if len(beats) < 2:
        sys.exit("Couldn't find a steady beat in this song.")

    pattern = get_pattern(args.rhythm, args.fill)
    per_bar = beats_per_bar(pattern)
    first = song.guess_first_beat(beats, onset, sr, per_bar)
    if args.shift is not None:
        first = (first + args.shift) % per_bar

    print(f"  about {bpm:.0f} BPM, {len(beats)} beats, beat 1 guessed at position {first}")
    print(f"  rhythm: {args.rhythm}{' (filled)' if args.fill else ''}")

    drums = mixer.render_drums(pattern, beats, sr, audio.shape[1], first)
    song_volume = 0.0 if args.drums_only else args.song_volume
    result = mixer.mix(audio, drums, song_volume, args.drum_volume)

    if args.out:
        sf.write(args.out, result.T, sr)
        print(f"Saved {args.out}")
        return

    print("Playing - press Ctrl+C to stop.")
    try:
        sd.play(result.T, sr)
        sd.wait()
    except KeyboardInterrupt:
        sd.stop()


if __name__ == "__main__":
    main()
