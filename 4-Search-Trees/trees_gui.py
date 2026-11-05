"""
Vizualizimi i pemëve të kërkimit (tkinter)
==========================================

Vizaton pemën e kërkimit për 8-Puzzle, Missionaries and Cannibals dhe
Rotating Workforce Scheduling, e ndërton nivel pas niveli dhe e thekson
rrugën drejt zgjidhjes. Përdor search_tree.py dhe tre problemet.

Ekzekutimi (nga folderi 4-Search-Trees):
    python trees_gui.py
"""

import os
import sys
import tkinter as tk

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))          # për gui_common.py

import eight_puzzle as ep                                        # noqa: E402
import gui_common as ui                                          # noqa: E402
import missionaries_cannibals as mc                              # noqa: E402
import rotating_workforce as rw                                  # noqa: E402
from search_tree import build_tree, count_by_status, level_counts  # noqa: E402

# problemi: (emri, krijuesi, thellësia fillestare, thellësia max, trajtimi i përsëritjeve, gjerësia, lartësia e nyjes)
PROBLEMS = {
    "puzzle": ("8-Puzzle", ep.EightPuzzle, 2, 4, "path", 64, 60),
    "mc": ("Missionaries and Cannibals", mc.MissionariesCannibals, 11, 15, "graph", 132, 40),
    "rws": ("Rotating Workforce", rw.RotatingWorkforce, 3, 5, "none", 0, 30),
}
GAP_X, GAP_Y = 14, 54


class TreeState:
    def __init__(self, key, depth):
        name, factory, _, _, repeated, width, height = PROBLEMS[key]
        self.key, self.name = key, name
        self.problem = factory()
        self.root, self.nodes = build_tree(self.problem, depth, repeated)
        self.visible = 1                    # sa nyje janë shfaqur deri tani (në rendin BFS)
        self.path = set()                   # nyjet në rrugën drejt zgjidhjes
        self.layout(width, height)

    def label(self, node):
        text = self.problem.format(node.state)
        if self.key == "puzzle":
            return text.replace(" / ", "\n")
        if self.key == "mc":
            m, c, b = node.state
            return f"({m},{c},{b})\n" + text.split(" ", 1)[1]
        return text

    def layout(self, width, height):
        """Gjethet vendosen me radhë majtas-djathtas; prindi në mes të fëmijëve."""
        if width == 0:                       # RWS: gjerësia sipas tekstit më të gjatë
            width = max(48, 9 * max(len(self.label(n)) for n in self.nodes) + 16)
        self.w, self.h = width, height
        self.pos = {}
        next_x = [20]

        def place(node):
            if not node.children:
                x = next_x[0] + width / 2
                next_x[0] += width + GAP_X
            else:
                for child in node.children:
                    place(child)
                xs = [self.pos[id(c)][0] for c in node.children]
                x = (min(xs) + max(xs)) / 2
            self.pos[id(node)] = (x, 20 + node.depth * (height + GAP_Y))

        place(self.root)
        self.width = next_x[0] + 20
        self.height = 40 + (max(n.depth for n in self.nodes) + 1) * (height + GAP_Y)


def reveal_events(st):
    """Shfaq nyjet një nga një, nivel pas niveli (rendi i ndërtimit, BFS)."""
    while st.visible < len(st.nodes):
        st.visible += 1
        yield "reveal"


class TreesWindow:
    def __init__(self, master):
        self.master = master
        body = ui.window_shell(master, "Search Trees – Pema e kërkimit")
        self.problem_key = tk.StringVar(value="puzzle")
        self.depth = tk.IntVar(value=2)
        self.state = None

        top = tk.Frame(body, bg=ui.BG)
        top.pack(fill="x")
        ui.choice_buttons(top, "Problemi", [("puzzle", "8-Puzzle"), ("mc", "Missionaries and Cannibals"),
                                            ("rws", "Rotating Workforce")],
                          self.problem_key, self.change_problem).pack(side="left")

        main = tk.Frame(body, bg=ui.BG)
        main.pack(fill="both", expand=True, pady=(12, 0))
        canvas_box = tk.Frame(main, bg=ui.BG, highlightbackground=ui.LIGHT_BORDER, highlightthickness=1)
        canvas_box.pack(side="left", fill="both", expand=True)
        self.canvas = tk.Canvas(canvas_box, bg=ui.BG, width=820, height=560, highlightthickness=0)
        xbar = tk.Scrollbar(canvas_box, orient="horizontal", command=self.canvas.xview)
        ybar = tk.Scrollbar(canvas_box, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=xbar.set, yscrollcommand=ybar.set)
        xbar.pack(side="bottom", fill="x")
        ybar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        right = tk.Frame(main, bg=ui.BG, width=300)
        right.pack(side="right", fill="y", padx=(20, 0))
        tk.Label(right, text="Thellësia e pemës", font=ui.FONT_BOLD, bg=ui.BG).pack(anchor="w")
        self.depth_box = tk.Spinbox(right, from_=1, to=4, textvariable=self.depth, width=5,
                                    font=ui.MONO_BOLD, command=self.rebuild)
        self.depth_box.pack(anchor="w", pady=(4, 10))

        self.animator = ui.Animator(master, self.make_generator, lambda e: None, self.render, self.reset_state)
        ui.bind_close(master, self.animator)
        ui.make_button(right, "Shfaq pemën e plotë", self.show_all, primary=True).pack(fill="x", pady=3)
        ui.make_button(right, "Ndërto nivel pas niveli", self.animate).pack(fill="x", pady=3)
        ui.make_button(right, "Gjej zgjidhjen", self.find_solution).pack(fill="x", pady=3)
        ui.make_button(right, "Rivendos", self.animator.reset).pack(fill="x", pady=3)
        tk.Label(right, text="Shpejtësia", font=ui.FONT_BOLD, bg=ui.BG).pack(anchor="w", pady=(10, 0))
        tk.Scale(right, from_=1, to=10, orient="horizontal", variable=self.animator.speed, showvalue=False,
                 bg=ui.BG, troughcolor=ui.LIGHT_BLUE, highlightthickness=0).pack(fill="x")

        self.stats = ui.StatsPanel(right, [
            ("nodes", "Nyje në pemë"), ("valid", "Të zgjeruara"), ("goal", "Qëllim"),
            ("repeated", "Përsëritje"), ("invalid", "Të pavlefshme"),
        ])
        self.stats.pack(fill="x", pady=(14, 0))
        self.levels = tk.StringVar()
        tk.Label(right, textvariable=self.levels, font=ui.FONT_SMALL, bg=ui.BG, fg=ui.MUTED,
                 wraplength=290, justify="left").pack(anchor="w", pady=(8, 0))
        self.message = tk.StringVar()
        tk.Label(right, textvariable=self.message, font=ui.FONT_BOLD, bg=ui.BG, fg=ui.DARK_BLUE,
                 wraplength=290, justify="left").pack(anchor="w", pady=(8, 0))

        legend = tk.Frame(right, bg=ui.BG)
        legend.pack(anchor="w", pady=(12, 0))
        for fill, outline, dash, text in [(ui.LIGHT_BLUE, ui.BLUE, (), "Rruga drejt zgjidhjes"),
                                          (ui.BLUE, ui.BLUE, (), "Gjendja qëllim"),
                                          (ui.PANEL, ui.GRAY, (3, 3), "Përsëritje"),
                                          (ui.LIGHT_ORANGE, ui.ORANGE, (), "E pavlefshme (X)")]:
            row = tk.Frame(legend, bg=ui.BG)
            row.pack(anchor="w", pady=1)
            swatch = tk.Canvas(row, width=16, height=16, bg=ui.BG, highlightthickness=0)
            swatch.create_rectangle(2, 2, 14, 14, fill=fill, outline=outline, dash=dash, width=2)
            swatch.pack(side="left")
            tk.Label(row, text=text, font=ui.FONT_SMALL, bg=ui.BG, fg=ui.MUTED).pack(side="left", padx=4)

        self.change_problem()

    # --- Veprimet ---
    def make_generator(self):
        return reveal_events(self.state)

    def reset_state(self):
        depth = max(1, min(self.depth.get(), PROBLEMS[self.problem_key.get()][3]))
        self.depth.set(depth)
        self.state = TreeState(self.problem_key.get(), depth)

    def change_problem(self):
        _, _, default, maximum, _, _, _ = PROBLEMS[self.problem_key.get()]
        self.depth.set(default)
        self.depth_box.config(to=maximum)
        self.rebuild()

    def rebuild(self):
        self.animator.reset()
        self.show_all()

    def show_all(self):
        self.animator.pause()
        self.state.visible = len(self.state.nodes)
        self.render()

    def animate(self):
        self.animator.reset()
        self.animator.start()

    def find_solution(self):
        st = self.state
        self.show_all()
        goal = next((n for n in st.nodes if n.status == "goal"), None)
        st.path = set()
        node = goal
        while node is not None:
            st.path.add(id(node))
            node = node.parent
        if goal:
            self.message.set(f"Zgjidhja në thellësinë {goal.depth}: " + " → ".join(goal.path_actions()))
        elif st.key == "rws":
            solution, count, _ = rw.dfs_count(rw.RotatingWorkforce(), find_first=False)
            rows = " / ".join("".join(solution[i:i + rw.DAYS]) for i in range(0, rw.LENGTH, rw.DAYS))
            self.message.set(f"Zgjidhjet janë në thellësinë {rw.LENGTH}, jashtë kësaj peme. "
                             f"DFS gjen {count} orare të vlefshme; i pari: {rows}")
        else:
            self.message.set("Qëllimi nuk është në këtë thellësi. Rritni thellësinë.")
        self.render(keep_message=True)

    # --- Vizatimi ---
    def render(self, keep_message=False):
        st = self.state
        visible = st.nodes[:st.visible]
        shown = {id(n) for n in visible}
        c = self.canvas
        c.delete("all")
        c.configure(scrollregion=(0, 0, st.width, st.height))
        w, h = st.w, st.h

        for node in visible:                                   # vijat dhe veprimet
            if node.parent is None:
                continue
            px, py = st.pos[id(node.parent)]
            x, y = st.pos[id(node)]
            on_path = id(node) in st.path
            c.create_line(px, py + h, x, y, fill=ui.BLUE if on_path else ui.GRAY, width=3 if on_path else 1)
            c.create_text((px + x) / 2 + 4, (py + h + y) / 2, text=str(node.action), anchor="w",
                          font=ui.FONT_SMALL, fill=ui.DARK_BLUE if on_path else ui.MUTED)

        for node in visible:                                   # nyjet
            x, y = st.pos[id(node)]
            fill, outline, fg, dash, width = ui.BG, ui.GRAY, ui.TEXT, (), 1
            if node.status == "goal":
                fill, outline, fg, width = ui.BLUE, ui.BLUE, "white", 2
            elif node.status == "repeated":
                fill, fg, dash = ui.PANEL, ui.MUTED, (3, 3)
            elif node.status:
                fill, outline, fg = ui.LIGHT_ORANGE, ui.ORANGE, ui.DARK_ORANGE
            elif id(node) in st.path:
                fill, outline, fg, width = ui.LIGHT_BLUE, ui.BLUE, ui.DARK_BLUE, 2
            c.create_rectangle(x - w / 2, y, x + w / 2, y + h, fill=fill, outline=outline, dash=dash, width=width)
            text = st.label(node)
            if node.status and node.status not in ("goal", "repeated"):
                text = "X " + text
            c.create_text(x, y + h / 2, text=text, fill=fg, font=ui.MONO, justify="center")

        stats = count_by_status(visible)
        self.stats.set("nodes", str(len(visible)))
        self.stats.set("valid", str(stats["valid"]))
        self.stats.set("goal", str(stats["goal"]))
        self.stats.set("repeated", str(stats["repeated"]))
        self.stats.set("invalid", str(stats["invalid"]))
        self.levels.set("Nyje në çdo nivel: " + ", ".join(map(str, level_counts(visible))))
        if not keep_message:
            if len(shown) < len(st.nodes):
                self.message.set("Pema po ndërtohet nivel pas niveli...")
            else:
                self.message.set(f"{st.name}: pema deri në thellësinë {self.depth.get()} ka {len(st.nodes)} nyje.")


def main():
    root = tk.Tk()
    TreesWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()