"""
Vizualizimi i Sudoku – BFS me Backtracking (tkinter)
====================================================

Tregon grid-in që po zgjerohet, qelizën e ardhshme me domenin e saj,
dhe grafikun e numrit të nyjeve në çdo nivel të pemës. Përdor funksionet
e sudoku_bfs.py.

Ekzekutimi (nga folderi 2-Sudoku-BFS):
    python sudoku_gui.py
"""

import math
import os
import sys
import tkinter as tk
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))          # për gui_common.py

import gui_common as ui                                                     # noqa: E402
from sudoku_bfs import PUZZLES, candidates, is_valid_puzzle, next_empty_cell  # noqa: E402

CELL = 46
CHART_W, CHART_H = 440, 170


class SearchState:
    def __init__(self, puzzle):
        self.puzzle = puzzle
        self.empty = puzzle.count("0")
        self.grid = puzzle                 # grid-i që po zgjerohet
        self.depth = 0
        self.cell = -1                     # qeliza e ardhshme
        self.values = []                   # domeni aktual i saj
        self.levels = [0] * (self.empty + 1)
        self.levels[0] = 1
        self.generated = 1
        self.expanded = 0
        self.dead_ends = 0
        self.queue_len = 1
        self.max_queue = 1
        self.solution = None
        self.stop_reason = None


def bfs_events(st):
    """BFS me backtracking, i njëjti algoritëm si në sudoku_bfs.py, si gjenerator."""
    if not is_valid_puzzle(st.puzzle):
        st.stop_reason = "invalid"
        yield "finish"
        return
    queue = deque([st.puzzle])
    while queue:
        grid = queue.popleft()                       # FIFO -> Breadth-First
        st.expanded += 1
        st.grid = grid
        st.depth = st.empty - grid.count("0")
        st.queue_len = len(queue)
        cell = next_empty_cell(grid)
        if cell == -1:                               # testi i qëllimit
            st.solution = grid
            st.cell, st.values = -1, []
            st.stop_reason = "solution"
            yield "solution"
            return
        values = candidates(grid, cell)
        st.cell, st.values = cell, values
        if not values:
            st.dead_ends += 1                        # BACKTRACKING: dega braktiset
            yield "dead_end"
            continue
        for value in values:
            queue.append(grid[:cell] + value + grid[cell + 1:])
        st.generated += len(values)
        st.levels[st.depth + 1] += len(values)
        st.queue_len = len(queue)
        st.max_queue = max(st.max_queue, len(queue))
        yield "expand"
    st.stop_reason = "exhausted"
    yield "finish"


class SudokuWindow:
    def __init__(self, master):
        self.master = master
        body = ui.window_shell(master, "Sudoku – BFS me Backtracking")
        self.level = tk.StringVar(value="hard")
        self.state = None

        left = tk.Frame(body, bg=ui.BG)
        left.pack(side="left", fill="y")
        right = tk.Frame(body, bg=ui.BG)
        right.pack(side="left", fill="both", expand=True, padx=(28, 0))

        self.title = tk.StringVar()
        tk.Label(left, textvariable=self.title, font=ui.FONT_TITLE, bg=ui.BG, fg=ui.TEXT).pack(anchor="w")
        self.subtitle = tk.StringVar()
        tk.Label(left, textvariable=self.subtitle, font=ui.FONT, bg=ui.BG, fg=ui.MUTED).pack(anchor="w")

        size = 9 * CELL + 8
        self.board = tk.Canvas(left, width=size, height=size, bg=ui.TEXT, highlightthickness=0)
        self.board.pack(anchor="w", pady=(12, 8))
        self.cells = []
        for i in range(81):
            r, c = divmod(i, 9)
            x = 4 + c * CELL + (c // 3) * 0
            y = 4 + r * CELL
            rect = self.board.create_rectangle(x + 1, y + 1, x + CELL - 1, y + CELL - 1, fill=ui.BG, outline="")
            text = self.board.create_text(x + CELL / 2, y + CELL / 2, text="", font=ui.MONO_BIG)
            self.cells.append((rect, text))
        for k in range(4):                                  # vijat e trasha të kutive 3 × 3
            p = 4 + k * 3 * CELL
            self.board.create_line(p, 2, p, size - 2, fill=ui.TEXT, width=4)
            self.board.create_line(2, p, size - 2, p, fill=ui.TEXT, width=4)

        legend = tk.Frame(left, bg=ui.BG)
        legend.pack(anchor="w")
        for color, outline, text in [(ui.BG, ui.GRAY, "Numër i dhënë"), (ui.LIGHT_BLUE, ui.LIGHT_BLUE, "Plotësuar nga BFS"),
                                     (ui.LIGHT_ORANGE, ui.ORANGE, "Qeliza e ardhshme")]:
            swatch = tk.Canvas(legend, width=14, height=14, bg=ui.BG, highlightthickness=0)
            swatch.create_rectangle(1, 1, 13, 13, fill=color, outline=outline, width=2)
            swatch.pack(side="left")
            tk.Label(legend, text=text, font=ui.FONT_SMALL, bg=ui.BG, fg=ui.MUTED).pack(side="left", padx=(4, 12))

        # --- Paneli djathtas ---
        ui.choice_buttons(right, "Niveli i Sudoku-së",
                          [("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")],
                          self.level, self.change_level).pack(fill="x")
        self.animator = ui.Animator(master, self.make_generator, lambda e: None, self.render, self.reset_state)
        ui.bind_close(master, self.animator)
        ui.control_bar(right, self.animator).pack(fill="x", pady=(12, 0))

        self.stats = ui.StatsPanel(right, [
            ("depth", "Niveli i pemës"), ("queue", "Nyje në rradhë"), ("generated", "Nyje të gjeneruara"),
            ("dead", "Degë të braktisura"), ("max_queue", "Rradha max"), ("time", "Koha"),
        ])
        self.stats.pack(fill="x", pady=(14, 0))

        tk.Label(right, text="Nyje në çdo nivel të pemës (shkallë logaritmike)", font=ui.FONT_BOLD,
                 bg=ui.BG).pack(anchor="w", pady=(14, 4))
        self.chart = tk.Canvas(right, width=CHART_W, height=CHART_H + 18, bg=ui.BG, highlightthickness=0)
        self.chart.pack(anchor="w")
        self.message = tk.StringVar()
        tk.Label(right, textvariable=self.message, font=ui.FONT_BOLD, bg=ui.BG, fg=ui.DARK_BLUE,
                 wraplength=440, justify="left").pack(anchor="w", pady=(10, 0))

        self.change_level()

    def make_generator(self):
        return bfs_events(self.state)

    def reset_state(self):
        self.state = SearchState(PUZZLES[self.level.get()])

    def change_level(self):
        self.animator.reset()

    def render(self):
        st = self.state
        grid = st.solution or st.grid
        for i, (rect, text) in enumerate(self.cells):
            given = st.puzzle[i] != "0"
            value = grid[i]
            if i == st.cell:
                domain = "".join(st.values) if st.values else "∅"
                self.board.itemconfig(rect, fill=ui.LIGHT_ORANGE, outline=ui.ORANGE, width=3)
                self.board.itemconfig(text, text=domain if len(domain) <= 3 else "?",
                                      fill=ui.DARK_ORANGE, font=ui.MONO_BOLD)
            elif given:
                self.board.itemconfig(rect, fill=ui.BG, outline="", width=1)
                self.board.itemconfig(text, text=value, fill=ui.TEXT, font=ui.MONO_BIG)
            elif value != "0":
                self.board.itemconfig(rect, fill=ui.LIGHT_BLUE, outline="", width=1)
                self.board.itemconfig(text, text=value, fill=ui.BLUE, font=("Consolas", 16))
            else:
                self.board.itemconfig(rect, fill=ui.BG, outline="", width=1)
                self.board.itemconfig(text, text="")

        # Grafiku i niveleve
        self.chart.delete("all")
        top = max(st.levels) or 1
        n = len(st.levels)
        bar_w = CHART_W / n
        for d, count in enumerate(st.levels):
            if count == 0:
                continue
            h = max(2, CHART_H * math.log10(count + 1) / math.log10(top + 1))
            color = ui.ORANGE if d == st.depth + 1 and st.stop_reason is None else (ui.BLUE if d <= st.depth else ui.GRAY)
            self.chart.create_rectangle(d * bar_w, CHART_H - h, (d + 1) * bar_w - 1, CHART_H, fill=color, outline="")
        self.chart.create_line(0, CHART_H, CHART_W, CHART_H, fill=ui.GRAY)
        for d in (0, n // 2, n - 1):
            self.chart.create_text(d * bar_w + bar_w / 2, CHART_H + 10, text=str(d), font=ui.FONT_SMALL, fill=ui.MUTED)

        self.title.set(f"Niveli {self.level.get().capitalize()} · niveli {st.depth} i pemës")
        self.subtitle.set(f"Numra të dhënë: {81 - st.empty} · qeliza të zbrazëta: {st.empty}")
        self.stats.set("depth", f"{st.depth} / {st.empty}")
        self.stats.set("queue", ui.fmt(st.queue_len))
        self.stats.set("generated", ui.fmt(st.generated))
        self.stats.set("dead", ui.fmt(st.dead_ends))
        self.stats.set("max_queue", ui.fmt(st.max_queue))
        self.stats.set("time", f"{self.animator.elapsed_seconds():.1f} s")

        if st.stop_reason == "solution":
            self.message.set(f"Zgjidhja u gjet në nivelin {st.empty}, pas {ui.fmt(st.generated)} nyjeve. "
                             "BFS i eksploroi të gjitha nivelet para saj, sepse zgjidhja është në nivelin e fundit.")
        elif st.stop_reason == "exhausted":
            self.message.set("Rradha u zbraz: puzzle-i nuk ka zgjidhje.")
        elif st.stop_reason == "invalid":
            self.message.set("Puzzle-i fillestar ka konflikte.")
        elif st.expanded == 0:
            self.message.set("Shtypni Nis ose Hap pas hapi. Për Hard, përdorni shpejtësi të lartë.")
        else:
            self.message.set(f"Qeliza e ardhshme ka domenin {{{', '.join(st.values)}}}."
                             if st.values else "Dega u braktis: qeliza e ardhshme nuk ka asnjë vlerë të lejuar.")


def main():
    root = tk.Tk()
    SudokuWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()