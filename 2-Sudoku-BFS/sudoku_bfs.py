"""
Sudoku Solver – Breadth-First Search (BFS) me Backtracking
==========================================================

Sudoku 9 × 9: çdo rresht, kolonë dhe kuti 3 × 3 duhet të përmbajë
numrat 1–9 saktësisht një herë. Programi i zgjidh tri nivele: Easy, Medium, Hard.

Modeli (shih README.md):
    Variabla      X(r,c) = vlera e qelizës së zbrazët në rreshtin r, kolonën c
    Domeni        {1, ..., 9}, i ngushtuar nga vlerat e fqinjëve
    Kufizimet     C1 rreshti, C2 kolona, C3 kutia 3×3: vlera të ndryshme;
                  C4 numrat e dhënë (givens) nuk ndryshohen
    Objektivi     f(S) = numri i konflikteve; zgjidhje = grid i plotë me f(S) = 0

Ekzekutimi:
    python sudoku_bfs.py                 # të tri nivelet
    python sudoku_bfs.py hard            # vetëm një nivel
    python sudoku_bfs.py medium --all    # BFS vazhdon deri në fund dhe numëron të gjitha zgjidhjet
"""

import sys
import time
from collections import deque
from math import factorial

# Grid-i ruhet si string me 81 karaktere, rresht pas rreshti; '0' = qelizë e zbrazët.
PUZZLES = {
    "easy": (
        "000260701"
        "680070090"
        "190004500"
        "820100040"
        "004602900"
        "050003028"
        "009300074"
        "040050036"
        "703018000"
    ),
    "medium": (
        "530070000"
        "600195000"
        "098000060"
        "800060003"
        "400803001"
        "700020006"
        "060000280"
        "000419005"
        "000080079"
    ),
    "hard": (
        "800000000"
        "003600000"
        "070090200"
        "050007000"
        "000045700"
        "000100030"
        "001000068"
        "008500010"
        "090000400"
    ),
}

DIGITS = "123456789"
MAX_GENERATED = 5_000_000      # kufi sigurie për memorien e BFS


# ---------------------------------------------------------------------------
# Fqinjët: për secilën qelizë, qelizat në të njëjtin rresht, kolonë dhe kuti
# ---------------------------------------------------------------------------

def build_peers():
    """Kthen listën PEERS, ku PEERS[i] janë 20 qelizat fqinje të qelizës i."""
    peers = []
    for i in range(81):
        r, c = divmod(i, 9)
        br, bc = 3 * (r // 3), 3 * (c // 3)
        cells = {r * 9 + k for k in range(9)}                                  # rreshti
        cells |= {k * 9 + c for k in range(9)}                                 # kolona
        cells |= {(br + a) * 9 + (bc + b) for a in range(3) for b in range(3)}  # kutia
        cells.discard(i)
        peers.append(tuple(sorted(cells)))
    return peers


PEERS = build_peers()


# ---------------------------------------------------------------------------
# Domeni dhe kufizimet
# ---------------------------------------------------------------------------

def candidates(grid, cell):
    """Domeni aktual i qelizës: vlerat që nuk shfaqen te fqinjët (C1, C2, C3)."""
    used = {grid[p] for p in PEERS[cell]}
    return [d for d in DIGITS if d not in used]


def is_valid_puzzle(grid):
    """Kontrollon që grid-i fillestar ka 81 karaktere dhe nuk ka konflikte."""
    if len(grid) != 81 or any(ch not in "0123456789" for ch in grid):
        return False
    return count_conflicts(grid) == 0


def next_empty_cell(grid):
    """Qeliza e ardhshme e zbrazët, me radhë rresht pas rreshti (-1 nëse s'ka)."""
    return grid.find("0")


# ---------------------------------------------------------------------------
# Funksioni objektiv dhe validimi
# ---------------------------------------------------------------------------

def count_conflicts(grid):
    """f(S): numri i çifteve të qelizave fqinje me të njëjtën vlerë (pa zerot)."""
    conflicts = 0
    for i, ch in enumerate(grid):
        if ch != "0":
            conflicts += sum(1 for p in PEERS[i] if p > i and grid[p] == ch)
    return conflicts


def calculate_objective(grid):
    """Kthen (f, e): f = numri i konflikteve, e = numri i qelizave të zbrazëta.
    Zgjidhje <=> f = 0 dhe e = 0."""
    return count_conflicts(grid), grid.count("0")


def validate_solution(solution, puzzle):
    """Validim i pavarur i zgjidhjes, nga fillimi. Kthen (True/False, gabimet)."""
    errors = []
    if len(solution) != 81 or "0" in solution:
        errors.append("Grid-i nuk është i plotë")
        return False, errors
    units = []
    for k in range(9):
        units.append(("Rreshti", k + 1, [k * 9 + c for c in range(9)]))
        units.append(("Kolona", k + 1, [r * 9 + k for r in range(9)]))
        br, bc = 3 * (k // 3), 3 * (k % 3)
        units.append(("Kutia", k + 1, [(br + a) * 9 + bc + b for a in range(3) for b in range(3)]))
    for name, number, cells in units:                                  # C1, C2, C3
        if sorted(solution[i] for i in cells) != list(DIGITS):
            errors.append(f"{name} {number} nuk përmban 1–9 nga një herë")
    for i, ch in enumerate(puzzle):                                    # C4
        if ch != "0" and solution[i] != ch:
            errors.append(f"Numri i dhënë në qelizën {divmod(i, 9)} është ndryshuar")
    return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# BFS me Backtracking
# ---------------------------------------------------------------------------

def bfs_solve(puzzle, find_all=False, max_generated=MAX_GENERATED):
    """Breadth-First Search me Backtracking.

    Nyje = grid i pjesshëm (string me 81 karaktere).
    Rradha (FIFO) i mban nyjet; pema eksplorohet nivel pas niveli.
    Fëmijët gjenerohen vetëm për vlerat e lejuara (C1–C3); nëse qeliza
    e ardhshme nuk ka asnjë vlerë të lejuar, nyja braktiset (dead end).

    Kthen (solutions, stats)."""
    stats = {"generated": 1, "expanded": 0, "dead_ends": 0,
             "max_queue": 1, "depth": puzzle.count("0"), "stop_reason": None}
    solutions = []
    if not is_valid_puzzle(puzzle):
        stats["stop_reason"] = "invalid_puzzle"
        return solutions, stats

    queue = deque([puzzle])                      # gjendja fillestare
    while queue:
        grid = queue.popleft()                   # FIFO -> Breadth-First
        stats["expanded"] += 1

        cell = next_empty_cell(grid)
        if cell == -1:                           # testi i qëllimit: grid i plotë
            solutions.append(grid)
            if not find_all:
                stats["stop_reason"] = "solution_found"
                return solutions, stats
            continue

        values = candidates(grid, cell)          # domeni aktual i qelizës
        if not values:
            stats["dead_ends"] += 1              # BACKTRACKING: dega braktiset
            continue

        for value in values:                     # zgjerimi: një fëmijë për çdo vlerë të lejuar
            queue.append(grid[:cell] + value + grid[cell + 1:])
        stats["generated"] += len(values)
        stats["max_queue"] = max(stats["max_queue"], len(queue))

        if stats["generated"] > max_generated:
            stats["stop_reason"] = "node_limit"
            return solutions, stats

    stats["stop_reason"] = "exhausted"           # e gjithë pema u kontrollua
    return solutions, stats


# ---------------------------------------------------------------------------
# Hapësira e kërkimit (Search Space)
# ---------------------------------------------------------------------------

def search_space(puzzle):
    """Madhësitë e hapësirës së kërkimit për një puzzle."""
    empty = puzzle.count("0")
    row_permutations = 1
    for r in range(9):
        row_permutations *= factorial(puzzle[r * 9:(r + 1) * 9].count("0"))
    reduced = 1
    for i, ch in enumerate(puzzle):
        if ch == "0":
            reduced *= len(candidates(puzzle, i))
    row_swaps = sum(puzzle[r * 9:(r + 1) * 9].count("0") * (puzzle[r * 9:(r + 1) * 9].count("0") - 1) // 2
                    for r in range(9))
    return {
        "empty": empty,
        "naive": 9 ** empty,                     # 9^k
        "row_permutations": row_permutations,    # prodhimi i k_r!
        "reduced": reduced,                      # prodhimi i |D(X)| fillestar
        "neighbors": row_swaps,                  # fqinjët në landscape (ndërrime brenda rreshtit)
    }


# ---------------------------------------------------------------------------
# Shfaqja e rezultateve
# ---------------------------------------------------------------------------

def sci(value):
    """Shkruan numrat e mëdhenj në formë shkencore, p.sh. 4.63e+48."""
    s = str(value)
    return f"{s[0]}.{s[1:3]}e+{len(s) - 1}" if value >= 10**6 else f"{value:,}"


def print_grid(grid):
    for r in range(9):
        row = ""
        for c in range(9):
            ch = grid[r * 9 + c]
            row += (ch if ch != "0" else ".") + " "
            if c in (2, 5):
                row += "| "
        print("  " + row.rstrip())
        if r in (2, 5):
            print("  ------+-------+------")


def solve_level(level, find_all=False):
    puzzle = PUZZLES[level]
    space = search_space(puzzle)

    print("=" * 66)
    print(f"SUDOKU – BFS me Backtracking | Niveli: {level.upper()}")
    print("=" * 66)
    print_grid(puzzle)
    print("-" * 66)
    print(f"Numra të dhënë (givens):          {81 - space['empty']}")
    print(f"Qeliza të zbrazëta (variabla):    {space['empty']}")
    print(f"Hapësira naive 9^k:               {sci(space['naive'])}")
    print(f"Permutacione për rresht:          {sci(space['row_permutations'])}")
    print(f"Pas domenit fillestar:            {sci(space['reduced'])}")
    print("-" * 66)

    start = time.time()
    solutions, stats = bfs_solve(puzzle, find_all)
    elapsed = time.time() - start

    if solutions:
        print("Zgjidhja:")
        print_grid(solutions[0])
        conflicts, empty = calculate_objective(solutions[0])
        valid, errors = validate_solution(solutions[0], puzzle)
        print("-" * 66)
        print(f"Objective function f(S):          {conflicts} konflikte, {empty} qeliza bosh")
        print(f"Zgjidhja është e vlefshme:        {'PO' if valid else 'JO'}")
        for error in errors:
            print("   -", error)
    else:
        print("Nuk u gjet zgjidhje.")
    if find_all and stats["stop_reason"] == "exhausted":
        print(f"Numri i zgjidhjeve:               {len(solutions)}")

    print(f"Thellësia e zgjidhjes (d):        {stats['depth']}")
    print(f"Nyje të gjeneruara:               {stats['generated']:,}")
    print(f"Nyje të zgjeruara:                {stats['expanded']:,}")
    print(f"Degë të braktisura (backtrack):   {stats['dead_ends']:,}")
    print(f"Madhësia max e rradhës (memoria): {stats['max_queue']:,}")
    print(f"Koha e ekzekutimit:               {elapsed:.2f} s")
    reasons = {
        "solution_found": "U gjet zgjidhja e parë.",
        "exhausted": "E gjithë pema u kontrollua.",
        "node_limit": "U arrit kufiri i nyjeve (memoria).",
        "invalid_puzzle": "Puzzle-i fillestar nuk është i vlefshëm.",
    }
    print(f"Arsyeja e ndalimit:               {reasons[stats['stop_reason']]}")
    print()


def main():
    args = [a.lower() for a in sys.argv[1:]]
    find_all = "--all" in args
    levels = [a for a in args if a in PUZZLES] or ["easy", "medium", "hard"]
    for level in levels:
        solve_level(level, find_all)


if __name__ == "__main__":
    main()