"""
8-Puzzle – Pema e kërkimit (Search Tree)
========================================

Tabela 3 × 3 me pllakat 1–8 dhe një vend bosh (0). Një veprim e zhvendos
vendin bosh lart, poshtë, majtas ose djathtas. Qëllimi është gjendja
    1 2 3
    4 5 6
    7 8 _

Formulimi (shih README.md):
    Gjendja       tuple me 9 numra, rresht pas rreshti; 0 = vendi bosh
    Veprimet      Up, Down, Left, Right (lëvizja e vendit bosh)
    Kostoja       1 për çdo veprim

Ekzekutimi:
    python eight_puzzle.py               # pema deri në thellësinë 2
    python eight_puzzle.py 3             # pema deri në thellësinë 3
    python eight_puzzle.py 2 --mermaid   # edhe kodi Mermaid për README
"""

import sys
from math import factorial

from search_tree import bfs_solution, build_tree, count_by_status, level_counts, print_tree, to_mermaid

GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 0)
START = (1, 2, 3, 4, 0, 6, 7, 5, 8)       # zgjidhet me 2 lëvizje
HARD_START = (8, 6, 7, 2, 5, 4, 3, 0, 1)  # gjendje me zgjidhje më të gjatë
CORNER = (0, 1, 2, 3, 4, 5, 6, 7, 8)      # vendi bosh në qoshe, për numërimin e nyjeve

MOVES = {"Up": -3, "Down": 3, "Left": -1, "Right": 1}


class EightPuzzle:
    def __init__(self, initial=START, goal=GOAL):
        self.initial = initial
        self.goal = goal

    def goal_test(self, state):
        return self.goal is not None and state == self.goal

    def expand(self, state):
        """Gjeneron fëmijët: vendi bosh lëviz brenda tabelës."""
        blank = state.index(0)
        row, col = divmod(blank, 3)
        children = []
        for action, delta in MOVES.items():
            if action == "Up" and row == 0:
                continue
            if action == "Down" and row == 2:
                continue
            if action == "Left" and col == 0:
                continue
            if action == "Right" and col == 2:
                continue
            target = blank + delta
            new = list(state)
            new[blank], new[target] = new[target], new[blank]
            children.append((action, tuple(new), None))
        return children

    def format(self, state):
        rows = [" ".join(str(x) if x else "_" for x in state[r * 3:r * 3 + 3]) for r in range(3)]
        return " / ".join(rows)


def is_solvable(state, goal=GOAL):
    """Një gjendje është e arritshme nga qëllimi vetëm nëse numri i inversioneve
    ka të njëjtin paritet si te qëllimi."""
    def inversions(s):
        tiles = [x for x in s if x]
        return sum(1 for i in range(len(tiles)) for j in range(i + 1, len(tiles)) if tiles[i] > tiles[j])
    return inversions(state) % 2 == inversions(goal) % 2


def state_space_size():
    return factorial(9) // 2                   # 181 440 gjendje të arritshme


def main():
    depth = 2
    mermaid = "--mermaid" in sys.argv
    for arg in sys.argv[1:]:
        if arg.isdigit():
            depth = int(arg)

    problem = EightPuzzle()
    print("=" * 66)
    print("8-PUZZLE – Pema e kërkimit")
    print("=" * 66)
    print(f"Gjendja fillestare:   {problem.format(problem.initial)}")
    print(f"Gjendja qëllim:       {problem.format(problem.goal)}")
    print(f"Gjendje të arritshme: {state_space_size():,} (9!/2)")
    print(f"Thellësia e pemës:    {depth}")
    print("-" * 66)

    root, nodes = build_tree(problem, depth, repeated="path")
    print(print_tree(root, problem))
    print("-" * 66)

    print("Nyje në çdo nivel, sipas trajtimit të gjendjeve të përsëritura:")
    for mode, name in (("none", "pa kontroll"), ("path", "pa kthim në rrugë"), ("graph", "pa përsëritje kudo")):
        _, all_nodes = build_tree(EightPuzzle(CORNER, goal=None), 6, repeated=mode)
        print(f"  {name:20s} {level_counts(all_nodes)}")
    print("  (pemë nga gjendja me vendin bosh në qoshe, deri në thellësinë 6)")
    print("-" * 66)

    stats = count_by_status(nodes)
    print(f"Nyje në pemë: {len(nodes)} | qëllim: {stats['goal']} | përsëritje: {stats['repeated']}")
    for name, start in (("START", START), ("HARD_START", HARD_START)):
        goal, generated = bfs_solution(EightPuzzle(start))
        if goal:
            print(f"BFS nga {name}: zgjidhje me {goal.depth} lëvizje, {generated:,} nyje të gjeneruara")
            if goal.depth <= 6:
                print(f"   Veprimet: {' -> '.join(goal.path_actions())}")
    if mermaid:
        print("-" * 66)
        print(to_mermaid(root, problem))
    print("=" * 66)


if __name__ == "__main__":
    main()