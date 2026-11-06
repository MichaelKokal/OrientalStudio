"""Oriental Studio - play instruments live, in any maqam.

Until the Casio is connected, the computer keyboard is the piano:

      W E   T Y U   O P          black keys
     A S D F G H J K L ; '       white keys
     Z / X  octave down / up     1-9  pick an instrument
     Up / Down  pick a maqam     Left / Right  move its root
     Space  start / stop rhythm  - / =  tempo      [ / ]  pick a rhythm

You can also click the keys and buttons on screen.
"""

import ctypes
import tkinter as tk

from oriental_studio import drums
from oriental_studio.instruments import INSTRUMENTS
from oriental_studio.keys import BLACK_KEYS, KEY_STEPS, NOTE_NAMES, WHITE_KEYS, WHITE_STEPS, label, note_name
from oriental_studio.maqamat import MAQAMAT, offsets, scale_notes
from oriental_studio.rhythm_player import SAMPLE_RATE, RhythmPlayer
from oriental_studio.rhythms import RHYTHMS
from oriental_studio.synth import Synth

BG = "#171026"
PANEL = "#241a3d"
TEXT = "#f4eee4"
MUTED = "#a99cc7"
ACCENT = "#fb7185"
GOLD = "#f5c76a"

WHITE_W, WHITE_H = 52, 170
BLACK_W, BLACK_H = 32, 106

RHYTHM_NAMES = list(RHYTHMS)


class App:
    def __init__(self, root):
        self.root = root
        self.synth = Synth()
        self.base = 60          # the note the A key plays (middle C)
        self.held = {}          # what's being pressed -> the note it started
        self.current = 0
        self.maqam = 0
        self.tonic = MAQAMAT[0].root
        self.rhythm = RhythmPlayer({
            "Darbuka": drums.evened(drums.kit(SAMPLE_RATE)),
            "Congas": drums.evened(drums.sound_bank_kit()),
        })

        root.title("Oriental Studio")
        root.configure(bg=BG, padx=24, pady=20)
        root.resizable(False, False)

        tk.Label(root, text="ORIENTAL STUDIO", bg=BG, fg=TEXT, font=("Segoe UI", 20, "bold")).pack(anchor="w")
        for hint in ["Z / X octave  ·  1–9 instrument  ·  ↑ ↓ maqam  ·  ← → root",
                     "Space start / stop  ·  − / = tempo  ·  [ / ] rhythm"]:
            tk.Label(root, text=hint, bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w")

        self.buttons = self._button_row("INSTRUMENT", [i.name for i in INSTRUMENTS], self.choose, numbered=True)
        self.maqam_buttons = self._button_row("MAQAM", [m.name for m in MAQAMAT], self.choose_maqam)
        self.rhythm_buttons = self._button_row("RHYTHM", [r.capitalize() for r in RHYTHM_NAMES],
                                               self.choose_rhythm, columns=6)
        self._build_rhythm_controls()
        self._build_piano()

        self.status = tk.Label(root, bg=BG, fg=MUTED, font=("Segoe UI", 10), anchor="w")
        self.status.pack(fill="x", pady=(12, 0))

        root.bind("<KeyPress>", self.key_down)
        root.bind("<KeyRelease>", self.key_up)
        root.bind("<FocusOut>", lambda e: self.release_all())
        root.protocol("WM_DELETE_WINDOW", self.quit)
        self.choose(0)
        self.choose_maqam(0)
        self.choose_rhythm(0)
        self._show_beat()

    # ---- layout ----

    def _button(self, parent, text, on_click, **grid):
        b = tk.Label(parent, text=text, bg=PANEL, fg=TEXT, font=("Segoe UI", 11), padx=12, pady=8, cursor="hand2")
        b.grid(sticky="ew", padx=3, pady=3, **grid)
        b.bind("<Button-1>", lambda e: on_click())
        return b

    def _build_rhythm_controls(self):
        row = tk.Frame(self.root, bg=BG)
        row.pack(fill="x", pady=(4, 0))
        self.play_button = self._button(row, "", self.toggle_rhythm, row=0, column=0)
        self._button(row, "−", lambda: self.change_tempo(-2), row=0, column=1)
        self.tempo_label = tk.Label(row, bg=BG, fg=TEXT, font=("Segoe UI", 11, "bold"), width=8)
        self.tempo_label.grid(row=0, column=2)
        self._button(row, "+", lambda: self.change_tempo(2), row=0, column=3)
        self.fill_button = self._button(row, "", self.toggle_fill, row=0, column=4)
        self.kit_button = self._button(row, "", self.next_kit, row=0, column=5)
        self.beat_dots = tk.Canvas(row, width=96, height=20, bg=BG, highlightthickness=0)
        self.beat_dots.grid(row=0, column=6, padx=(10, 0))
        self._show_rhythm_controls()

    def _button_row(self, title, names, on_click, numbered=False, columns=5):
        tk.Label(self.root, text=title, bg=BG, fg=MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(10, 2))
        frame = tk.Frame(self.root, bg=BG)
        frame.pack(fill="x")
        buttons = []
        for i, name in enumerate(names):
            text = f"{i + 1}  {name}" if numbered else name
            buttons.append(self._button(frame, text, lambda i=i: on_click(i), row=i // columns, column=i % columns))
        for col in range(columns):
            frame.columnconfigure(col, weight=1, uniform=title)
        return buttons

    def _build_piano(self):
        width = WHITE_W * len(WHITE_KEYS)
        self.piano = tk.Canvas(self.root, width=width, height=WHITE_H + 2, bg=BG, highlightthickness=0)
        self.piano.pack(pady=(16, 0))
        self.key_shapes = {}    # semitone -> (shape id, normal colour)
        self.shape_steps = {}   # shape id -> semitone
        self.dots = {}          # semitone -> dot marking it as part of the maqam

        def add_key(step, x, w, h, fill, text_fill, size, key):
            shape = self.piano.create_rectangle(x, 1, x + w, h, fill=fill, outline=BG, width=2)
            self.piano.create_text(x + w / 2, h - 16, text=label(key), fill=text_fill,
                                   font=("Segoe UI", size, "bold"), state="disabled")
            cx, cy = x + w / 2, h - 38
            self.dots[step] = self.piano.create_oval(cx - 5, cy - 5, cx + 5, cy + 5, outline="", state="hidden")
            self.key_shapes[step] = (shape, fill)
            self.shape_steps[shape] = step

        for i, (key, step) in enumerate(zip(WHITE_KEYS, WHITE_STEPS)):
            add_key(step, i * WHITE_W + 1, WHITE_W - 2, WHITE_H, TEXT, "#6b5a8e", 11, key)
        for key, step in BLACK_KEYS.items():
            # A black key sits on the line after the white key just below it.
            x = (WHITE_STEPS.index(step - 1) + 1) * WHITE_W - BLACK_W / 2
            add_key(step, x, BLACK_W, BLACK_H, PANEL, MUTED, 9, key)

        legend = tk.Frame(self.root, bg=BG)
        legend.pack(anchor="w", pady=(8, 0))
        for colour, text in [(ACCENT, "in the maqam"), (GOLD, "quarter tone flat")]:
            tk.Label(legend, text="●", bg=BG, fg=colour, font=("Segoe UI", 10)).pack(side="left")
            tk.Label(legend, text=text + "    ", bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(side="left")

        self.piano.bind("<ButtonPress-1>", self.click_down)
        self.piano.bind("<ButtonRelease-1>", lambda e: self.release("mouse"))

    # ---- playing ----

    def press(self, source, step):
        note = self.base + step
        if source in self.held or not 0 <= note <= 127:
            return
        self.synth.note_on(note)
        self.held[source] = note
        self._light(step, True)
        self._show_status(note)

    def release(self, source):
        note = self.held.pop(source, None)
        if note is None:
            return
        self.synth.note_off(note)
        self._light(note - self.base, False)

    def release_all(self):
        for source in list(self.held):
            self.release(source)

    def key_down(self, event):
        key = event.keysym.lower()
        if key in KEY_STEPS:
            self.press(key, KEY_STEPS[key])   # held keys repeat; press() ignores the repeats
        elif key == "z":
            self.shift_octave(-12)
        elif key == "x":
            self.shift_octave(12)
        elif key.isdigit() and 1 <= int(key) <= len(INSTRUMENTS):
            self.choose(int(key) - 1)
        elif key in ("up", "down"):
            self.choose_maqam((self.maqam + (1 if key == "down" else -1)) % len(MAQAMAT))
        elif key in ("left", "right"):
            self.set_tonic(self.tonic + (1 if key == "right" else -1))
        elif key == "space":
            self.toggle_rhythm()
        elif key in ("minus", "equal"):
            self.change_tempo(2 if key == "equal" else -2)
        elif key in ("bracketleft", "bracketright"):
            current = RHYTHM_NAMES.index(self.rhythm.rhythm)
            self.choose_rhythm((current + (1 if key == "bracketright" else -1)) % len(RHYTHM_NAMES))

    def key_up(self, event):
        self.release(event.keysym.lower())

    def click_down(self, event):
        hits = self.piano.find_overlapping(event.x, event.y, event.x, event.y)
        steps = [self.shape_steps[h] for h in hits if h in self.shape_steps]
        if steps:
            self.press("mouse", steps[-1])   # the last one is on top, so black keys win

    def shift_octave(self, amount):
        if 24 <= self.base + amount <= 96:
            self.release_all()
            self.base += amount
            self._show_status()

    def choose(self, index):
        self.release_all()
        self.current = index
        inst = INSTRUMENTS[index]
        self.synth.set_instrument(inst.bank, inst.preset)
        self._highlight(self.buttons, index)
        self._show_status()

    def choose_maqam(self, index):
        self.maqam = index
        self._highlight(self.maqam_buttons, index)
        self.set_tonic(MAQAMAT[index].root)

    def set_tonic(self, tonic):
        """Start the maqam on a different note. Its quarter tones move with it."""
        self.tonic = tonic % 12
        maqam = MAQAMAT[self.maqam]
        flats = offsets(maqam, self.tonic)
        self.synth.set_tuning(flats)
        in_scale = scale_notes(maqam, self.tonic)
        for step, dot in self.dots.items():
            pc = (self.base + step) % 12
            colour = GOLD if flats[pc] else ACCENT
            self.piano.itemconfigure(dot, fill=colour, state="normal" if pc in in_scale else "hidden")
        self._show_status()

    # ---- rhythm ----

    def choose_rhythm(self, index):
        self.rhythm.set_rhythm(RHYTHM_NAMES[index])
        self._highlight(self.rhythm_buttons, index)

    def toggle_rhythm(self):
        if self.rhythm.playing:
            self.rhythm.stop()
        else:
            self.rhythm.start()
        self._show_rhythm_controls()

    def change_tempo(self, amount):
        self.rhythm.bpm = max(40, min(240, self.rhythm.bpm + amount))
        self._show_rhythm_controls()

    def toggle_fill(self):
        self.rhythm.set_rhythm(fill=not self.rhythm.fill)
        self._show_rhythm_controls()

    def next_kit(self):
        names = list(self.rhythm.kits)
        self.rhythm.kit = names[(names.index(self.rhythm.kit) + 1) % len(names)]
        self._show_rhythm_controls()

    # ---- display ----

    def _show_rhythm_controls(self):
        r = self.rhythm
        self.play_button.configure(text="■  Stop" if r.playing else "▶  Start",
                                   bg=ACCENT if r.playing else PANEL, fg=BG if r.playing else TEXT)
        self.tempo_label.configure(text=f"{r.bpm} BPM")
        self.fill_button.configure(text=f"Fill: {'on' if r.fill else 'off'}")
        self.kit_button.configure(text=f"Kit: {r.kit}")

    def _show_beat(self):
        """Light up the current beat, about 30 times a second."""
        self.beat_dots.delete("all")
        for i in range(self.rhythm.beats_in_bar):
            on = self.rhythm.playing and i == self.rhythm.beat
            colour = (GOLD if i == 0 else ACCENT) if on else PANEL
            self.beat_dots.create_oval(4 + i * 24, 3, 18 + i * 24, 17, fill=colour, outline="")
        self.root.after(30, self._show_beat)

    def _highlight(self, buttons, index):
        for i, b in enumerate(buttons):
            b.configure(bg=ACCENT if i == index else PANEL, fg=BG if i == index else TEXT)

    def _light(self, step, on):
        if step in self.key_shapes:
            shape, normal = self.key_shapes[step]
            self.piano.itemconfigure(shape, fill=ACCENT if on else normal)

    def _show_status(self, playing=None):
        inst = INSTRUMENTS[self.current]
        maqam = MAQAMAT[self.maqam]
        sound = f" (using a {inst.stand_in} sound for now)" if inst.stand_in else ""
        scale = "No maqam" if not maqam.notes else f"{maqam.name} on {NOTE_NAMES[self.tonic]}"
        text = f"{inst.name}{sound}   ·   {scale}   ·   A key = {note_name(self.base)}"
        if playing is not None:
            flat = offsets(maqam, self.tonic)[playing % 12] != 0
            text += f"   ·   playing {note_name(playing, flat)}"
        self.status.configure(text=text)

    def quit(self):
        self.release_all()
        self.rhythm.close()
        self.synth.close()
        self.root.destroy()


def main():
    try:
        # Without this, Windows blurs the window on high-resolution screens.
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError):
        pass
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
