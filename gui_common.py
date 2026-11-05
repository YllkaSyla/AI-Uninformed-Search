"""
Pjesët e përbashkëta të vizualizimit me tkinter
===============================================

Përdoret nga golfers_gui.py, sudoku_gui.py, latin_gui.py dhe trees_gui.py.
Përmban ngjyrat, fontet, butonat, panelin e statistikave dhe klasën Animator,
e cila e ekzekuton algoritmin hap pas hapi.

Si funksionon animacioni:
    Çdo dritare ka një gjenerator (funksion me `yield`) që ekzekuton algoritmin
    dhe jep një "ngjarje" për çdo hap: p.sh. ("place", grupi) ose ("backtrack", ...).
    Animator-i merr disa ngjarje në çdo cikël të `after()`, ia jep dritares
    për t'i zbatuar, dhe pastaj e rivizaton dritaren një herë.
"""

import time
import tkinter as tk

# --- Ngjyrat (të njëjtat si në pamjen e propozuar) ---------------------------
BG = "#FFFFFF"
PANEL = "#F9FAFB"
TEXT = "#111827"
MUTED = "#4B5563"
BORDER = "#D1D5DB"
LIGHT_BORDER = "#E5E7EB"
BLUE = "#1D4ED8"
DARK_BLUE = "#1E3A8A"
LIGHT_BLUE = "#DBEAFE"
SKY = "#93C5FD"
ORANGE = "#C2410C"
DARK_ORANGE = "#9A3412"
LIGHT_ORANGE = "#FFF7ED"
PEACH = "#FDBA74"
EMPTY = "#F3F4F6"
GRAY = "#9CA3AF"

# --- Fontet -------------------------------------------------------------------
FONT = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_SMALL = ("Segoe UI", 9)
MONO = ("Consolas", 10)
MONO_BOLD = ("Consolas", 11, "bold")
MONO_BIG = ("Consolas", 16, "bold")

# Shpejtësia: (vonesa në ms, ngjarje për cikël) për pozicionet 1..10 të rrëshqitësit
SPEEDS = [(500, 1), (250, 1), (120, 1), (60, 1), (30, 1),
          (15, 2), (5, 10), (1, 50), (1, 500), (1, 5000)]


def fmt(number):
    """1234567 -> '1 234 567'"""
    return f"{number:,}".replace(",", " ")


def make_button(parent, text, command, primary=False, width=None):
    button = tk.Button(
        parent, text=text, command=command, font=FONT_BOLD,
        bg=BLUE if primary else BG, fg="white" if primary else TEXT,
        activebackground=DARK_BLUE if primary else LIGHT_BLUE,
        activeforeground="white" if primary else TEXT,
        relief="flat" if primary else "solid", bd=1, padx=12, pady=8,
        cursor="hand2", highlightthickness=0,
    )
    if width:
        button.config(width=width)
    return button


def header(parent, title, subtitle=""):
    """Titulli dhe nëntitulli në krye të një dritareje."""
    frame = tk.Frame(parent, bg=BG)
    tk.Label(frame, text=title, font=FONT_TITLE, bg=BG, fg=TEXT, anchor="w").pack(anchor="w")
    if subtitle:
        tk.Label(frame, text=subtitle, font=FONT, bg=BG, fg=MUTED, anchor="w").pack(anchor="w")
    return frame


class StatsPanel(tk.Frame):
    """Lista e statistikave: emri majtas, vlera djathtas."""

    def __init__(self, parent, rows):
        super().__init__(parent, bg=BG, highlightbackground=LIGHT_BORDER, highlightthickness=1)
        self.values = {}
        for i, (key, label) in enumerate(rows):
            row = tk.Frame(self, bg=BG)
            row.pack(fill="x", padx=12, pady=6)
            tk.Label(row, text=label, font=FONT, bg=BG, fg=MUTED).pack(side="left")
            var = tk.StringVar(value="–")
            tk.Label(row, textvariable=var, font=MONO_BOLD, bg=BG, fg=TEXT).pack(side="right")
            self.values[key] = var
            if i < len(rows) - 1:
                tk.Frame(self, bg=LIGHT_BORDER, height=1).pack(fill="x")

    def set(self, key, value):
        self.values[key].set(value)


class Animator:
    """Ekzekuton një gjenerator ngjarjesh me `after()`, hap pas hapi.

    make_generator()   krijon gjeneratorin e algoritmit
    apply_event(ev)    zbaton një ngjarje në gjendjen e dritares
    render()           rivizaton dritaren
    on_reset()         kthen dritaren në gjendjen fillestare
    """

    def __init__(self, widget, make_generator, apply_event, render, on_reset):
        self.widget = widget
        self.make_generator = make_generator
        self.apply_event = apply_event
        self.render = render
        self.on_reset = on_reset
        self.speed = tk.IntVar(value=5)
        self.generator = None
        self.running = False
        self.finished = False
        self.elapsed = 0.0
        self._started_at = None
        self._job = None

    def _ensure_generator(self):
        if self.generator is None:
            self.generator = self.make_generator()

    def _next(self):
        """Zbaton ngjarjen e ardhshme. Kthen False kur algoritmi ka mbaruar."""
        try:
            event = next(self.generator)
        except StopIteration:
            self.finished = True
            return False
        self.apply_event(event)
        return True

    def elapsed_seconds(self):
        if self._started_at is not None:
            return self.elapsed + (time.time() - self._started_at)
        return self.elapsed

    def start(self):
        if self.running or self.finished:
            return
        self._ensure_generator()
        self.running = True
        self._started_at = time.time()
        self._tick()

    def pause(self):
        if self._job is not None:
            self.widget.after_cancel(self._job)
            self._job = None
        if self._started_at is not None:
            self.elapsed += time.time() - self._started_at
            self._started_at = None
        self.running = False

    def step(self):
        self.pause()
        if self.finished:
            return
        self._ensure_generator()
        self._next()
        self.render()

    def reset(self):
        self.pause()
        self.generator = None
        self.finished = False
        self.elapsed = 0.0
        self.on_reset()
        self.render()

    def _tick(self):
        if not self.running:
            return
        delay, batch = SPEEDS[self.speed.get() - 1]
        for _ in range(batch):
            if not self._next():
                self.pause()
                break
        self.render()
        if self.running:
            self._job = self.widget.after(delay, self._tick)


def control_bar(parent, animator):
    """Butonat Nis / Pauzë / Hap pas hapi / Rivendos dhe rrëshqitësi i shpejtësisë."""
    frame = tk.Frame(parent, bg=BG)
    buttons = tk.Frame(frame, bg=BG)
    buttons.pack(fill="x")
    for i, (text, command, primary) in enumerate([
        ("Nis", animator.start, True),
        ("Pauzë", animator.pause, False),
        ("Hap pas hapi", animator.step, False),
        ("Rivendos", animator.reset, False),
    ]):
        make_button(buttons, text, command, primary).grid(row=i // 2, column=i % 2, sticky="ew", padx=3, pady=3)
    buttons.columnconfigure(0, weight=1)
    buttons.columnconfigure(1, weight=1)
    tk.Label(frame, text="Shpejtësia", font=FONT_BOLD, bg=BG, fg=TEXT).pack(anchor="w", pady=(10, 0))
    tk.Scale(frame, from_=1, to=10, orient="horizontal", variable=animator.speed, showvalue=False,
             bg=BG, troughcolor=LIGHT_BLUE, highlightthickness=0, activebackground=BLUE,
             sliderrelief="flat").pack(fill="x")
    return frame


def choice_buttons(parent, label, options, variable, command):
    """Një rresht butonash ku zgjidhet një opsion (p.sh. Easy / Medium / Hard)."""
    frame = tk.Frame(parent, bg=BG)
    tk.Label(frame, text=label, font=FONT_BOLD, bg=BG, fg=TEXT).pack(anchor="w")
    row = tk.Frame(frame, bg=BG)
    row.pack(fill="x", pady=(4, 0))
    buttons = {}

    def refresh():
        for value, button in buttons.items():
            selected = variable.get() == value
            button.config(bg=LIGHT_BLUE if selected else BG, fg=DARK_BLUE if selected else TEXT,
                          relief="solid", bd=2 if selected else 1)

    def choose(value):
        variable.set(value)
        refresh()
        command()

    for value, text in options:
        button = tk.Button(row, text=text, font=FONT_BOLD, command=lambda v=value: choose(v),
                           padx=10, pady=6, cursor="hand2", highlightthickness=0)
        button.pack(side="left", padx=(0, 6))
        buttons[value] = button
    refresh()
    return frame


def bind_close(master, animator):
    """Kur mbyllet dritarja, animacioni ndalet para se të shkatërrohet dritarja."""
    def close():
        animator.pause()
        master.destroy()
    master.protocol("WM_DELETE_WINDOW", close)


def window_shell(master, title):
    """Përgatit dritaren (Tk ose Toplevel) dhe kthen kornizën kryesore."""
    master.title(title)
    master.configure(bg=BG)
    body = tk.Frame(master, bg=BG, padx=20, pady=16)
    body.pack(fill="both", expand=True)
    return body