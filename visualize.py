"""
Vizualizimi i detyrave – menuja kryesore (tkinter)
==================================================

Hap një dritare me katër detyrat. Çdo buton hap vizualizimin e detyrës
në një dritare të re.

Ekzekutimi (nga folderi AI-Uninformed-Search):
    python visualize.py
"""

import os
import sys
import tkinter as tk

ROOT = os.path.dirname(os.path.abspath(__file__))
for folder in ("1-Social-Golfers-DFS", "2-Sudoku-BFS", "3-Latin-Square-IDDFS", "4-Search-Trees"):
    sys.path.insert(0, os.path.join(ROOT, folder))
sys.path.insert(0, ROOT)

import gui_common as ui  # noqa: E402

TASKS = [
    ("1", "Social Golfers", "DFS me Backtracking",
     "32 lojtarë në 8 grupe me nga 4. Orari ndërtohet\ngrup pas grupi, javë pas jave.",
     "5 javë të vlefshme · kufiri teorik 10", "golfers_gui", "GolfersWindow"),
    ("2", "Sudoku", "BFS me Backtracking",
     "Tri nivele: Easy, Medium, Hard. Pema eksplorohet\nnivel pas niveli, dhe shihet si rritet rradha.",
     "Hard: 2 068 781 nyje · rradha max 356 812", "sudoku_gui", "SudokuWindow"),
    ("3", "Latin Square", "IDDFS me Backtracking",
     "Katror latin n × n. Çdo iteracion rrit limitin\ne thellësisë dhe fillon nga e para.",
     "n = 5: 26 iteracione · 13 505 923 nyje", "latin_gui", "LatinWindow"),
    ("4", "Search Trees", "Ndërtimi i pemës",
     "8-Puzzle, Missionaries and Cannibals dhe\nRotating Workforce: pema rritet nivel pas niveli.",
     "8-Puzzle: 17 nyje · Misionarët: 49 nyje", "trees_gui", "TreesWindow"),
]


def open_task(module_name, class_name, master):
    """Importon modulin e detyrës vetëm kur hapet, dhe e shfaq në dritare të re."""
    module = __import__(module_name)
    window = tk.Toplevel(master)
    getattr(module, class_name)(window)


def main():
    root = tk.Tk()
    body = ui.window_shell(root, "AI – Teknikat e painformuara të kërkimit")

    tk.Label(body, text="DETYRA E PARË SEMESTRALE · INTELIGJENCA ARTIFICIALE 2026/27",
             font=ui.FONT_BOLD, bg=ui.BG, fg=ui.ORANGE).pack(anchor="w")
    tk.Label(body, text="Teknikat e painformuara të kërkimit", font=("Segoe UI", 22, "bold"),
             bg=ui.BG, fg=ui.TEXT).pack(anchor="w", pady=(4, 2))
    tk.Label(body, text="Zgjidhni një detyrë për ta parë algoritmin duke punuar hap pas hapi.",
             font=ui.FONT, bg=ui.BG, fg=ui.MUTED).pack(anchor="w")

    grid = tk.Frame(body, bg=ui.BG)
    grid.pack(fill="both", expand=True, pady=(18, 10))
    for i, (number, title, tag, description, stat, module, cls) in enumerate(TASKS):
        card = tk.Frame(grid, bg=ui.BG, highlightbackground=ui.LIGHT_BORDER, highlightthickness=1, padx=18, pady=16)
        card.grid(row=i // 2, column=i % 2, sticky="nsew", padx=8, pady=8)
        head = tk.Frame(card, bg=ui.BG)
        head.pack(anchor="w")
        tk.Label(head, text=number, font=ui.FONT_BOLD, bg=ui.BLUE, fg="white", width=3, pady=4).pack(side="left")
        tk.Label(head, text=title, font=("Segoe UI", 14, "bold"), bg=ui.BG, fg=ui.TEXT).pack(side="left", padx=10)
        tk.Label(card, text=tag, font=ui.FONT_SMALL, bg=ui.LIGHT_BLUE, fg=ui.DARK_BLUE, padx=8, pady=2).pack(anchor="w", pady=(10, 6))
        tk.Label(card, text=description, font=ui.FONT, bg=ui.BG, fg=ui.MUTED, justify="left").pack(anchor="w")
        tk.Label(card, text=stat, font=ui.MONO, bg=ui.BG, fg=ui.TEXT).pack(anchor="w", pady=(6, 10))
        ui.make_button(card, "Hap vizualizimin", lambda m=module, c=cls: open_task(m, c, root),
                       primary=True).pack(fill="x")
    grid.columnconfigure(0, weight=1)
    grid.columnconfigure(1, weight=1)

    footer = tk.Frame(body, bg=ui.BG)
    footer.pack(fill="x")
    tk.Label(footer, text="Çdo detyrë mund të hapet edhe veçmas, p.sh. python golfers_gui.py brenda folderit të saj.",
             font=ui.FONT_SMALL, bg=ui.BG, fg=ui.MUTED).pack(side="left")
    root.mainloop()


if __name__ == "__main__":
    main()