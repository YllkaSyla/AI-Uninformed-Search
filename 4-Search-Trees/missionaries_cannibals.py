"""
Missionaries and Cannibals – Pema e kërkimit (Search Tree)
==========================================================

3 misionarë dhe 3 kanibalë duhet të kalojnë lumin me një varkë që merr
më së shumti 2 persona. Në asnjë breg, kanibalët nuk duhet të jenë më shumë
se misionarët (kur në atë breg ka të paktën një misionar).

Formulimi (shih README.md):
    Gjendja       (M, C, B): misionarët dhe kanibalët në bregun e majtë,
                  B = 1 nëse varka është majtas, 0 nëse djathtas
    Fillestare    (3, 3, 1)
    Qëllimi       (0, 0, 0)
    Veprimet      varka bart (1M), (2M), (1C), (2C) ose (1M1C)
    Kostoja       1 për çdo kalim

Ekzekutimi:
    python missionaries_cannibals.py             # pema e plotë (pa përsëritje)
    python missionaries_cannibals.py --mermaid   # edhe kodi Mermaid për README
"""

import sys

from search_tree import bfs_solution, build_tree, count_by_status, level_counts, print_tree, to_mermaid

TOTAL = 3                                       # 3 misionarë, 3 kanibalë
BOAT = [(1, 0), (2, 0), (0, 1), (0, 2), (1, 1)]  # (misionarë, kanibalë) në varkë


def is_safe(m, c):
    """Asnjë breg nuk ka më shumë kanibalë se misionarë (kur ka misionarë)."""
    left_ok = m == 0 or m >= c
    right_ok = (TOTAL - m) == 0 or (TOTAL - m) >= (TOTAL - c)
    return left_ok and right_ok


class MissionariesCannibals:
    initial = (TOTAL, TOTAL, 1)
    goal = (0, 0, 0)

    def goal_test(self, state):
        return state == self.goal

    def expand(self, state):
        """Gjeneron fëmijët. Kalimet e pamundura (më shumë persona se në breg)
        nuk gjenerohen; kalimet ku kanibalët i hanë misionarët gjenerohen
        si fëmijë të pavlefshëm, që të shihen në pemë."""
        m, c, b = state
        sign = -1 if b == 1 else 1                 # varka majtas -> personat largohen nga majtas
        children = []
        for dm, dc in BOAT:
            nm, nc = m + sign * dm, c + sign * dc
            if not (0 <= nm <= TOTAL and 0 <= nc <= TOTAL):
                continue                           # nuk ka aq persona në breg
            action = f"{dm}M{dc}C" + ("→" if b == 1 else "←")
            invalid = None if is_safe(nm, nc) else "misionarët hahen"
            children.append((action, (nm, nc, 1 - b), invalid))
        return children

    def format(self, state):
        m, c, b = state
        left = "M" * m + "C" * c
        right = "M" * (TOTAL - m) + "C" * (TOTAL - c)
        boat = "V|" if b == 1 else "|V"          # V = varka
        return f"({m},{c},{b}) {left or '-'} {boat} {right or '-'}"


def valid_states():
    """Të gjitha gjendjet (M, C, B) që respektojnë kushtin e sigurisë."""
    return [(m, c, b) for m in range(TOTAL + 1) for c in range(TOTAL + 1) for b in (0, 1)
            if is_safe(m, c)]


def main():
    mermaid = "--mermaid" in sys.argv
    problem = MissionariesCannibals()

    print("=" * 70)
    print("MISSIONARIES AND CANNIBALS – Pema e kërkimit")
    print("=" * 70)
    print(f"Gjendje të mundshme (M, C, B):   {(TOTAL + 1) ** 2 * 2}")
    print(f"Gjendje të sigurta:              {len(valid_states())}")
    print("-" * 70)

    root, nodes = build_tree(problem, max_depth=20, repeated="graph")
    print(print_tree(root, problem))
    print("-" * 70)

    stats = count_by_status(nodes)
    print(f"Nyje në pemë:                    {len(nodes)}")
    print(f"  të vlefshme dhe të zgjeruara:  {stats['valid']}")
    print(f"  qëllim:                        {stats['goal']}")
    print(f"  përsëritje (nuk zgjerohen):    {stats['repeated']}")
    print(f"  të pavlefshme (hahen):         {stats['invalid']}")
    print(f"Nyje në çdo nivel:               {level_counts(nodes)}")

    goal, generated = bfs_solution(problem)
    print(f"Zgjidhja më e shkurtër (BFS):    {goal.depth} kalime, {generated} nyje të gjeneruara")
    for i, state in enumerate(goal.path_states()):
        action = "" if i == 0 else goal.path_actions()[i - 1]
        print(f"  {i:2d}. {action:7s} {problem.format(state)}")

    _, path_nodes = build_tree(problem, max_depth=11, repeated="path")
    _, none_nodes = build_tree(problem, max_depth=11, repeated="none")
    print("-" * 70)
    print("Nyje deri në thellësinë 11, sipas trajtimit të gjendjeve të përsëritura:")
    print(f"  pa kontroll:         {len(none_nodes):,}")
    print(f"  pa kthim në rrugë:   {len(path_nodes):,}")
    print(f"  pa përsëritje kudo:  {len(nodes):,}")
    if mermaid:
        print("-" * 70)
        print(to_mermaid(root, problem))
    print("=" * 70)


if __name__ == "__main__":
    main()