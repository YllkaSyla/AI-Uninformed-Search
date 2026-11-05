"""
Vizualizimi i Latin Square – IDDFS me Backtracking (tkinter)
============================================================

Tregon katrorin që plotësohet, vlerat që vendosen dhe hiqen (backtracking),
dhe numrin e nyjeve në çdo iteracion të IDDFS.

Ekzekutimi (nga folderi 3-Latin-Square-IDDFS):
    python latin_gui.py
"""

import math
import os
import sys
import tkinter as tk

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))          # për gui_common.py

import gui_common as ui                              # noqa: E402
from latin_square_iddfs import CUTOFF, FAILURE       # noqa: E402

# Ngjyra e sfondit dhe e tekstit për vlerat 1..6
VALUE_COLORS = {1: (ui.BLUE, "white"), 2: (ui.SKY, ui.TEXT), 3: (ui.PEACH, ui.TEXT),
                4: (ui.ORANGE, "white"), 5: ("#E5E7EB", ui.TEXT), 6: ("#0F766E", "white")}
CHART_W = 360


class SearchState:
    def __init__(self, n, step):
        self.n, self.step = n, step
        self.grid = [[0] * n for _ in range(n)]
        self.row_used = [[False] * (n + 1) for _ in range(n)]
        self.col_used = [[False] * (n + 1) for _ in range(n)]
        self.limit = 0
        self.depth = 0
        self.cell = None                  # qeliza e fundit që u ndryshua
        self.iterations = []              # [limiti, nyjet, rezultati]
        self.iter_nodes = 0
        self.nodes = 0
        self.backtracks = 0
        self.stop_reason = None


def iddfs_events(st):
    """IDDFS me backtracking, i njëjti algoritëm si në latin_square_iddfs.py, si gjenerator."""
    n = st.n

    def dls(depth, limit):
        st.nodes += 1
        st.iter_nodes += 1
        if depth == n * n:
            return True
        if depth == limit:
            return CUTOFF
        r, c = divmod(depth, n)
        cutoff = False
        for v in range(1, n + 1):
            if st.row_used[r][v] or st.col_used[c][v]:
                continue                                  # shkel C1 ose C2
            st.grid[r][c] = v
            st.row_used[r][v] = st.col_used[c][v] = True
            st.depth, st.cell = depth + 1, (r, c)
            yield "assign"
            result = yield from dls(depth + 1, limit)
            if result is True:
                return True
            if result == CUTOFF:
                cutoff = True
            st.grid[r][c] = 0                             # BACKTRACKING
            st.row_used[r][v] = st.col_used[c][v] = False
            st.backtracks += 1
            st.depth = depth
            yield "backtrack"
        return CUTOFF if cutoff else FAILURE

    limit = 0
    while True:
        limit = min(limit, n * n)
        st.limit, st.iter_nodes = limit, 0
        st.iterations.append([limit, 0, "..."])
        yield "iteration"
        result = yield from dls(0, limit)
        st.iterations[-1] = [limit, st.iter_nodes, result]
        if result is True:
            st.stop_reason = "solution"
            yield "finish"
            return
        if result == FAILURE:
            st.stop_reason = "no_solution"
            yield "finish"
            return
        limit += st.step


class LatinWindow:
    def __init__(self, master):
        self.master = master
        body = ui.window_shell(master, "Latin Square – IDDFS me Backtracking")
        self.n = tk.IntVar(value=5)
        self.step = tk.StringVar(value="1")
        self.state = None

        left = tk.Frame(body, bg=ui.BG)
        left.pack(side="left", fill="y")
        right = tk.Frame(body, bg=ui.BG)
        right.pack(side="left", fill="both", expand=True, padx=(28, 0))

        self.title = tk.StringVar()
        tk.Label(left, textvariable=self.title, font=ui.FONT_TITLE, bg=ui.BG, fg=ui.TEXT).pack(anchor="w")
        self.subtitle = tk.StringVar()
        tk.Label(left, textvariable=self.subtitle, font=ui.FONT, bg=ui.BG, fg=ui.MUTED).pack(anchor="w")
        self.board = tk.Canvas(left, width=420, height=420, bg=ui.BG, highlightthickness=0)
        self.board.pack(anchor="w", pady=(12, 8))
        self.explain = tk.StringVar()
        tk.Label(left, textvariable=self.explain, font=ui.FONT, bg=ui.BG, fg=ui.MUTED,
                 wraplength=420, justify="left").pack(anchor="w")

        options = tk.Frame(right, bg=ui.BG)
        options.pack(fill="x")
        ui.choice_buttons(options, "Rendi n", [(3, "3"), (4, "4"), (5, "5"), (6, "6")],
                          self.n, self.change_options).pack(side="left", anchor="n")
        ui.choice_buttons(options, "Hapi i limitit", [("1", "1 (klasik)"), ("n", "n (një rresht)")],
                          self.step, self.change_options).pack(side="left", anchor="n", padx=(20, 0))

        self.animator = ui.Animator(master, self.make_generator, lambda e: None, self.render, self.reset_state)
        ui.bind_close(master, self.animator)
        ui.control_bar(right, self.animator).pack(fill="x", pady=(12, 0))

        self.stats = ui.StatsPanel(right, [
            ("limit", "Limiti aktual"), ("depth", "Thellësia"), ("nodes", "Nyje gjithsej"),
            ("backtracks", "Backtracking"), ("time", "Koha"),
        ])
        self.stats.pack(fill="x", pady=(14, 0))

        tk.Label(right, text="Nyje në çdo iteracion (shkallë logaritmike)", font=ui.FONT_BOLD,
                 bg=ui.BG).pack(anchor="w", pady=(14, 4))
        self.chart = tk.Canvas(right, width=CHART_W + 140, height=380, bg=ui.BG, highlightthickness=0)
        self.chart.pack(anchor="w")
        self.message = tk.StringVar()
        tk.Label(right, textvariable=self.message, font=ui.FONT_BOLD, bg=ui.BG, fg=ui.DARK_BLUE,
                 wraplength=480, justify="left").pack(anchor="w", pady=(8, 0))

        self.change_options()

    def make_generator(self):
        return iddfs_events(self.state)

    def reset_state(self):
        n = self.n.get()
        step = n if self.step.get() == "n" else 1
        self.state = SearchState(n, step)

    def change_options(self):
        self.animator.reset()

    def render(self):
        st = self.state
        n = st.n
        size = min(76, 400 // n)
        self.board.delete("all")
        for r in range(n):
            for c in range(n):
                x, y = 4 + c * (size + 6), 4 + r * (size + 6)
                v = st.grid[r][c]
                current = st.cell == (r, c) and st.stop_reason is None
                if v:
                    fill, fg = VALUE_COLORS[v]
                    self.board.create_rectangle(x, y, x + size, y + size, fill=fill,
                                                outline=ui.ORANGE if current else fill, width=4 if current else 1)
                    self.board.create_text(x + size / 2, y + size / 2, text=str(v), fill=fg,
                                           font=("Consolas", max(12, size // 3), "bold"))
                else:
                    self.board.create_rectangle(x, y, x + size, y + size, outline=ui.GRAY, dash=(3, 3))

        self.chart.delete("all")
        rows = st.iterations
        if rows:
            row_h = max(6, min(16, 370 // len(rows)))
            top = max(max(it[1] for it in rows), st.iter_nodes, 10)
            for i, (limit, nodes, result) in enumerate(rows):
                if result == "...":
                    nodes = st.iter_nodes
                y = i * row_h
                w = max(2, CHART_W * math.log10(nodes + 1) / math.log10(top + 1))
                color = ui.ORANGE if result is True else (ui.BLUE if result == "..." else ui.SKY)
                self.chart.create_text(30, y + row_h / 2, text=str(limit), anchor="e", font=ui.FONT_SMALL, fill=ui.MUTED)
                self.chart.create_rectangle(36, y + 1, 36 + w, y + row_h - 2, fill=color, outline="")
                self.chart.create_text(36 + CHART_W + 100, y + row_h / 2, text=ui.fmt(nodes), anchor="e",
                                       font=ui.FONT_SMALL, fill=ui.TEXT)

        status = {"solution": "U gjet zgjidhja", "no_solution": "Nuk ka zgjidhje"}.get(st.stop_reason)
        self.title.set(status or f"Iteracioni {len(rows)} · limiti {st.limit}")
        self.subtitle.set(f"n = {n} · hapi i limitit = {st.step} · thellësia e zgjidhjes = {n * n}")
        self.stats.set("limit", f"{st.limit} / {n * n}")
        self.stats.set("depth", str(st.depth))
        self.stats.set("nodes", ui.fmt(st.nodes))
        self.stats.set("backtracks", ui.fmt(st.backtracks))
        self.stats.set("time", f"{self.animator.elapsed_seconds():.1f} s")

        if st.stop_reason == "solution":
            last = rows[-1][1]
            self.message.set(f"Iteracioni i fundit e gjeti zgjidhjen pas {ui.fmt(last)} nyjeve. "
                             f"Gjithsej u vizituan {ui.fmt(st.nodes)} nyje, sepse çdo zgjidhje është në thellësinë {n * n}.")
            self.explain.set("Çdo rresht dhe çdo kolonë përmban 1.." + str(n) + " saktësisht një herë.")
        elif rows:
            self.message.set("Shufrat e kaltra të çelëta: iteracione që përfunduan me cutoff, pa zgjidhje.")
            self.explain.set("Kufiza portokalli tregon qelizën që sapo u ndryshua. "
                             "Kur një degë nuk ka vazhdim, vlera hiqet (backtracking) dhe provohet tjetra.")
        else:
            self.message.set("Shtypni Nis ose Hap pas hapi. Për n = 5, përdorni shpejtësi të lartë.")
            self.explain.set("")
        if n == 6 and st.stop_reason is None:
            self.message.set(self.message.get() + " Kujdes: për n = 6 IDDFS mund të zgjasë shumë.")


def main():
    root = tk.Tk()
    LatinWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()