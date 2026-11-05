"""
Vizualizimi i Social Golfers – DFS me Backtracking (tkinter)
============================================================

Tregon orarin që ndërtohet grup pas grupi, matricën e çifteve dhe çdo
kthim prapa (backtracking). Përdor funksionet e social_golfers.py.

Ekzekutimi (nga folderi 1-Social-Golfers-DFS):
    python golfers_gui.py
"""

import os
import sys
import tkinter as tk
from collections import deque
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))          # për gui_common.py

import gui_common as ui                              # noqa: E402
from social_golfers import group_pairs, upper_bound  # noqa: E402

INSTANCES = {
    "8x4": (8, 4),
    "4x4": (4, 4),
    "5x3": (5, 3),
    "3x3": (3, 3),
}
WEEK_COLORS = ["#1E3A8A", "#1D4ED8", "#3B82F6", "#60A5FA", "#93C5FD",
               "#0F766E", "#14B8A6", "#5EEAD4", "#6B7280", "#D1D5DB"]


class SearchState:
    """Gjendja e kërkimit që e ndryshon gjeneratori dhe e lexon dritarja."""

    def __init__(self, g, p):
        self.g, self.p, self.n = g, p, g * p
        self.max_weeks = upper_bound(self.n, p)
        self.weeks = []           # javët e plota
        self.current = []         # grupet e javës aktuale
        self.placed = set()
        self.used_pairs = set()
        self.met = {}             # çifti -> java në të cilën u takua (1, 2, ...)
        self.candidate = None     # grupi që po kontrollohet
        self.conflict = None
        self.nodes = 0
        self.backtracks = 0
        self.rejected = 0
        self.best = []
        self.stop_reason = None
        self.log = deque(maxlen=9)
        self.show_rejected = False


def dfs_events(st):
    """DFS me backtracking, i njëjti algoritëm si në social_golfers.py,
    por si gjenerator: jep një ngjarje për çdo hap që të vizatohet."""

    def label():
        return f"J{len(st.weeks) + 1}·G{len(st.current) + 1}"

    def show(items):
        return "(" + ",".join(map(str, items)) + ")"

    def add(group):
        week = len(st.weeks) + 1
        st.current.append(group)
        st.placed.update(group)
        for pair in group_pairs(group):
            st.used_pairs.add(pair)
            st.met[pair] = week

    def remove():
        group = st.current.pop()
        st.placed.difference_update(group)
        for pair in group_pairs(group):
            st.used_pairs.discard(pair)
            st.met.pop(pair, None)
        return group

    def dfs():
        st.nodes += 1
        if len(st.current) == st.g:                        # java u plotësua
            st.weeks.append(st.current)
            st.current = []
            if len(st.weeks) > len(st.best):
                st.best = [list(w) for w in st.weeks]
                st.log.append(f"Java {len(st.weeks)} u plotësua: më i miri = {len(st.best)} javë")
            yield "week"
            if len(st.weeks) == st.max_weeks:
                st.stop_reason = "upper_bound"
                return True
            saved = st.placed
            st.placed = set()
            if (yield from dfs()):
                return True
            st.current = st.weeks.pop()                    # kthim në javën e mëparshme
            st.placed = saved
            return False

        available = [x for x in range(st.n) if x not in st.placed]
        first = available[0]
        for rest in combinations(available[1:], st.p - 1):
            group = (first,) + rest
            conflict = next((pair for pair in group_pairs(group) if pair in st.used_pairs), None)
            if conflict:
                st.rejected += 1
                if st.show_rejected:
                    st.candidate, st.conflict = group, conflict
                    st.log.append(f"{label()} {show(group)} refuzohet: {show(conflict)} në javën {st.met[conflict]}")
                    yield "reject"
                continue
            st.candidate, st.conflict = group, None
            st.log.append(f"{label()} {show(group)} pranohet")
            add(group)
            yield "place"
            if (yield from dfs()):
                return True
            removed = remove()
            st.backtracks += 1
            st.candidate = None
            st.log.append(f"BACKTRACK: hiqet {show(removed)}")
            yield "backtrack"
        st.candidate = None
        return False

    for j in range(st.g):                                  # java 1 fiksohet (SB3)
        add(tuple(range(j * st.p, (j + 1) * st.p)))
    st.log.append("Java 1 fiksohet: (0..p-1), (p..2p-1), ...")
    yield "start"
    if not (yield from dfs()):
        st.stop_reason = "exhausted"
    yield "finish"


class GolfersWindow:
    def __init__(self, master):
        self.master = master
        body = ui.window_shell(master, "Social Golfers – DFS me Backtracking")
        self.instance = tk.StringVar(value="8x4")
        self.show_rejected = tk.BooleanVar(value=False)
        self.state = None

        left = tk.Frame(body, bg=ui.BG)
        left.pack(side="left", fill="both", expand=True)
        right = tk.Frame(body, bg=ui.BG, width=320)
        right.pack(side="right", fill="y", padx=(20, 0))

        self.title = tk.StringVar()
        tk.Label(left, textvariable=self.title, font=ui.FONT_TITLE, bg=ui.BG, fg=ui.TEXT).pack(anchor="w")
        self.subtitle = tk.StringVar()
        tk.Label(left, textvariable=self.subtitle, font=ui.FONT, bg=ui.BG, fg=ui.MUTED).pack(anchor="w")

        self.table = tk.Canvas(left, bg=ui.BG, highlightthickness=0)
        self.table.pack(anchor="w", pady=(12, 12))

        bottom = tk.Frame(left, bg=ui.BG)
        bottom.pack(anchor="w", fill="x")
        matrix_box = tk.Frame(bottom, bg=ui.BG)
        matrix_box.pack(side="left", anchor="n")
        self.matrix_title = tk.StringVar()
        tk.Label(matrix_box, textvariable=self.matrix_title, font=ui.FONT_BOLD, bg=ui.BG).pack(anchor="w")
        self.matrix = tk.Canvas(matrix_box, bg=ui.BG, highlightthickness=0, width=290, height=290)
        self.matrix.pack(anchor="w", pady=(6, 0))

        legend = tk.Frame(bottom, bg=ui.BG)
        legend.pack(side="left", anchor="n", padx=(24, 0))
        tk.Label(legend, text="Si lexohet matrica", font=ui.FONT_BOLD, bg=ui.BG).pack(anchor="w")
        text = ("Kutia (a, b) ngjyroset kur lojtarët a dhe b\n"
                "kanë luajtur bashkë. Çdo javë ka ngjyrën e vet;\n"
                "java që po ndërtohet është portokalli.\n\n"
                "Asnjë kuti nuk ngjyroset dy herë:\n"
                "ky është kushti m(a, b) ≤ 1.")
        tk.Label(legend, text=text, font=ui.FONT, bg=ui.BG, fg=ui.MUTED, justify="left").pack(anchor="w")

        # --- Paneli djathtas ---
        ui.choice_buttons(right, "Instanca (g × p)",
                          [("8x4", "8×4"), ("4x4", "4×4"), ("5x3", "5×3"), ("3x3", "3×3")],
                          self.instance, self.change_instance).pack(fill="x")
        self.animator = ui.Animator(master, self.make_generator, self.apply_event, self.render, self.reset_state)
        ui.bind_close(master, self.animator)
        ui.control_bar(right, self.animator).pack(fill="x", pady=(12, 0))
        tk.Checkbutton(right, text="Shfaq edhe kandidatët e refuzuar", variable=self.show_rejected,
                       command=self.toggle_rejected, font=ui.FONT, bg=ui.BG,
                       activebackground=ui.BG).pack(anchor="w", pady=(6, 0))

        self.stats = ui.StatsPanel(right, [
            ("nodes", "Nyje të vizituara"), ("backtracks", "Backtracking"),
            ("rejected", "Kandidatë të refuzuar"), ("weeks", "Javë të plota"),
            ("best", "Më i miri"), ("pairs", "Çifte të përdorura"),
            ("bound", "Kufiri teorik"), ("time", "Koha"),
        ])
        self.stats.pack(fill="x", pady=(14, 0))

        self.message = tk.StringVar()
        tk.Label(right, textvariable=self.message, font=ui.FONT_BOLD, bg=ui.BG, fg=ui.DARK_BLUE,
                 wraplength=300, justify="left").pack(anchor="w", pady=(10, 0))
        tk.Label(right, text="Hapat e fundit", font=ui.FONT_BOLD, bg=ui.BG).pack(anchor="w", pady=(10, 0))
        self.log = tk.Listbox(right, font=ui.MONO, height=9, width=44, bd=0,
                              highlightthickness=1, highlightbackground=ui.LIGHT_BORDER)
        self.log.pack(fill="x")

        self.change_instance()

    # --- Animacioni ---
    def make_generator(self):
        return dfs_events(self.state)

    def apply_event(self, event):
        pass                                   # gjeneratori e ndryshon vetë self.state

    def toggle_rejected(self):
        if self.state:
            self.state.show_rejected = self.show_rejected.get()

    def reset_state(self):
        g, p = INSTANCES[self.instance.get()]
        self.state = SearchState(g, p)
        self.state.show_rejected = self.show_rejected.get()
        self.build_canvases()

    def change_instance(self):
        self.animator.reset()

    # --- Vizatimi ---
    def build_canvases(self):
        st = self.state
        self.cell_w = max(60, 14 * st.p + 10)
        self.cell_h = 26
        rows = st.max_weeks
        self.table.delete("all")
        self.table.config(width=60 + st.g * (self.cell_w + 4), height=24 + rows * (self.cell_h + 4))
        for j in range(st.g):
            self.table.create_text(60 + j * (self.cell_w + 4) + self.cell_w / 2, 10,
                                   text=f"Grupi {j + 1}", font=ui.FONT_SMALL, fill=ui.MUTED)
        self.table_cells = []
        for r in range(rows):
            y = 24 + r * (self.cell_h + 4)
            self.table.create_text(26, y + self.cell_h / 2, text=f"Java {r + 1}", font=ui.FONT_SMALL, fill=ui.TEXT)
            row = []
            for j in range(st.g):
                x = 60 + j * (self.cell_w + 4)
                rect = self.table.create_rectangle(x, y, x + self.cell_w, y + self.cell_h, outline=ui.BORDER)
                text = self.table.create_text(x + self.cell_w / 2, y + self.cell_h / 2, text="", font=ui.MONO)
                row.append((rect, text))
            self.table_cells.append(row)

        self.matrix.delete("all")
        size = max(4, 288 // st.n)
        self.matrix.config(width=size * st.n + 2, height=size * st.n + 2)
        self.matrix_cells = {}
        for a in range(st.n):
            for b in range(st.n):
                self.matrix_cells[(a, b)] = self.matrix.create_rectangle(
                    1 + b * size, 1 + a * size, (b + 1) * size, (a + 1) * size, outline="", fill=ui.EMPTY)
        self.matrix_title.set(f"Matrica e çifteve {st.n} × {st.n}")

    def render(self):
        st = self.state
        building = len(st.weeks) + 1
        for r, row in enumerate(self.table_cells):
            if r < len(st.weeks):
                groups, kind = st.weeks[r], "done"
            elif r == len(st.weeks):
                groups, kind = st.current, "current"
            else:
                groups, kind = [], "empty"
            for j, (rect, text) in enumerate(row):
                if j < len(groups):
                    self.table.itemconfig(rect, fill=ui.LIGHT_BLUE, outline=ui.LIGHT_BLUE, dash=())
                    self.table.itemconfig(text, text=",".join(map(str, groups[j])), fill=ui.DARK_BLUE)
                elif kind == "current" and j == len(groups) and st.candidate and st.conflict:
                    self.table.itemconfig(rect, fill=ui.LIGHT_ORANGE, outline=ui.ORANGE, dash=())
                    self.table.itemconfig(text, text=",".join(map(str, st.candidate)), fill=ui.DARK_ORANGE)
                else:
                    self.table.itemconfig(rect, fill=ui.BG, outline=ui.BORDER, dash=(3, 3))
                    self.table.itemconfig(text, text="")
            if kind == "current" and st.current:
                rect, text = row[len(st.current) - 1]
                self.table.itemconfig(rect, fill=ui.LIGHT_ORANGE, outline=ui.ORANGE)
                self.table.itemconfig(text, fill=ui.DARK_ORANGE)

        for (a, b), item in self.matrix_cells.items():
            if a == b:
                color = ui.GRAY
            else:
                week = st.met.get((min(a, b), max(a, b)))
                if week is None:
                    color = ui.EMPTY
                elif week == building:
                    color = ui.ORANGE
                else:
                    color = WEEK_COLORS[(week - 1) % len(WEEK_COLORS)]
            self.matrix.itemconfig(item, fill=color)

        self.title.set(f"Orari: java {min(building, st.max_weeks)}, grupi {len(st.current) + 1} nga {st.g}"
                       if st.stop_reason is None else f"Orari përfundimtar: {len(st.best)} javë")
        self.subtitle.set(f"n = {st.n} · g = {st.g} · p = {st.p}")
        self.stats.set("nodes", ui.fmt(st.nodes))
        self.stats.set("backtracks", ui.fmt(st.backtracks))
        self.stats.set("rejected", ui.fmt(st.rejected))
        self.stats.set("weeks", str(len(st.weeks)))
        self.stats.set("best", f"{len(st.best)} javë")
        self.stats.set("pairs", f"{len(st.used_pairs)} / {st.n * (st.n - 1) // 2}")
        self.stats.set("bound", f"{st.max_weeks} javë")
        self.stats.set("time", f"{self.animator.elapsed_seconds():.1f} s")

        if st.stop_reason == "upper_bound":
            self.message.set(f"U arrit kufiri teorik: {len(st.best)} javë. Rezultati është optimal.")
        elif st.stop_reason == "exhausted":
            self.message.set(f"E gjithë pema u kontrollua: maksimumi është {len(st.best)} javë (i dëshmuar).")
        elif st.best:
            self.message.set(f"Më i miri deri tani: {len(st.best)} javë. Kërkimi vazhdon; "
                             f"rezultati nuk është dëshmuar optimal.")
        else:
            self.message.set("Shtypni Nis ose Hap pas hapi.")

        self.log.delete(0, "end")
        for line in st.log:
            self.log.insert("end", line)


def main():
    root = tk.Tk()
    GolfersWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()