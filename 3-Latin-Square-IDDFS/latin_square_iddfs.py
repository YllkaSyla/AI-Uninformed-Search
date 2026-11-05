"""
Latin Square – Iterative Deepening Depth-First Search (IDDFS) me Backtracking
=============================================================================

Katror latin: grid n × n i mbushur me numrat 1..n, ku çdo numër shfaqet
saktësisht një herë në çdo rresht dhe në çdo kolonë.

Modeli (shih README.md):
    Variabla      X(r,c) = numri në rreshtin r dhe kolonën c
    Domeni        {1, ..., n}
    Kufizimet     C1 rreshti, C2 kolona: vlera të ndryshme
    Objektivi     f(S) = numri i përsëritjeve në rreshta dhe kolona;
                  zgjidhje = grid i plotë me f(S) = 0

Ekzekutimi:
    python latin_square_iddfs.py              # n = 5, IDDFS klasik (limiti rritet me 1)
    python latin_square_iddfs.py 4            # n = 4
    python latin_square_iddfs.py 6 --step=6   # limiti rritet me një rresht të tërë
"""

import sys
import time
from math import factorial

CUTOFF = "cutoff"      # DLS arriti limitin e thellësisë pa zgjidhje
FAILURE = "failure"    # DLS kontrolloi gjithë pemën deri në limit dhe nuk ka zgjidhje

# Numri i njohur i katrorëve latinë L(n) (OEIS A002860), për krahasim
KNOWN_LATIN_SQUARES = {1: 1, 2: 2, 3: 12, 4: 576, 5: 161280, 6: 812851200}


# ---------------------------------------------------------------------------
# IDDFS me Backtracking
# ---------------------------------------------------------------------------

class LatinSquareIDDFS:
    """Nyje e kërkimit = grid i pjesshëm, i plotësuar rresht pas rreshti.
    Thellësia e nyjes = numri i qelizave të plotësuara (0 .. n²)."""

    def __init__(self, n, step=1, time_limit=120):
        self.n = n
        self.step = step
        self.time_limit = time_limit

        # Gjendja e kërkimit
        self.grid = [[0] * n for _ in range(n)]
        self.row_used = [[False] * (n + 1) for _ in range(n)]   # row_used[r][v]
        self.col_used = [[False] * (n + 1) for _ in range(n)]   # col_used[c][v]

        # Statistikat
        self.nodes = 0
        self.backtracks = 0
        self.iterations = []        # (limiti, nyjet në iteracion, rezultati)
        self.stop_reason = None
        self.start_time = None

    # --- Kufizimet, zgjerimi dhe kthimi prapa ---------------------------

    def is_consistent(self, r, c, v):
        """C1 dhe C2: vlera v nuk është përdorur në rreshtin r dhe kolonën c."""
        return not self.row_used[r][v] and not self.col_used[c][v]

    def assign(self, r, c, v):
        self.grid[r][c] = v
        self.row_used[r][v] = True
        self.col_used[c][v] = True

    def backtrack(self, r, c, v):
        """BACKTRACKING: heq vlerën v nga qeliza (r, c)."""
        self.grid[r][c] = 0
        self.row_used[r][v] = False
        self.col_used[c][v] = False
        self.backtracks += 1

    # --- Depth-Limited Search ------------------------------------------

    def dls(self, depth, limit):
        """DFS që nuk shkon më thellë se 'limit'.
        Kthen True (zgjidhje), CUTOFF ose FAILURE."""
        self.nodes += 1

        if time.time() - self.start_time > self.time_limit:
            raise TimeoutError

        if depth == self.n * self.n:          # testi i qëllimit: të gjitha qelizat plot
            return True
        if depth == limit:                    # u arrit limiti i thellësisë
            return CUTOFF

        r, c = divmod(depth, self.n)          # qeliza e ardhshme, rresht pas rreshti
        cutoff_occurred = False
        for v in range(1, self.n + 1):
            if not self.is_consistent(r, c, v):
                continue                      # shkel kufizimin -> nuk zgjerohet
            self.assign(r, c, v)              # zgjerimi i gjendjes
            result = self.dls(depth + 1, limit)
            if result is True:
                return True
            if result == CUTOFF:
                cutoff_occurred = True
            self.backtrack(r, c, v)           # provo vlerën e ardhshme
        return CUTOFF if cutoff_occurred else FAILURE

    # --- Iterative Deepening -------------------------------------------

    def iddfs(self):
        """Ekzekuton DLS me limit = 0, step, 2·step, ... deri në n²."""
        self.start_time = time.time()
        limit = 0
        try:
            while True:
                limit = min(limit, self.n * self.n)
                before = self.nodes
                result = self.dls(0, limit)
                self.iterations.append((limit, self.nodes - before, result))
                if result is True:
                    self.stop_reason = "solution_found"
                    return True
                if result == FAILURE:
                    self.stop_reason = "no_solution"
                    return False
                limit += self.step
        except TimeoutError:
            self.iterations.append((limit, self.nodes - before, "time_limit"))
            self.stop_reason = "time_limit"
            return False


# ---------------------------------------------------------------------------
# Funksioni objektiv dhe validimi
# ---------------------------------------------------------------------------

def calculate_objective(grid):
    """f(S) = Σ_rreshta (n − vlera të ndryshme) + Σ_kolona (n − vlera të ndryshme).
    f(S) = 0  <=>  grid-i i plotë është katror latin."""
    n = len(grid)
    f = 0
    for i in range(n):
        f += n - len(set(grid[i]))                          # përsëritje në rreshtin i
        f += n - len({grid[r][i] for r in range(n)})        # përsëritje në kolonën i
    return f


def validate_latin_square(grid):
    """Validim i pavarur, nga fillimi. Kthen (True/False, lista e gabimeve)."""
    n = len(grid)
    errors = []
    expected = list(range(1, n + 1))
    for r in range(n):
        if len(grid[r]) != n:
            errors.append(f"Rreshti {r + 1} nuk ka {n} qeliza")
        elif sorted(grid[r]) != expected:
            errors.append(f"Rreshti {r + 1} nuk përmban 1..{n} nga një herë")
    if not errors:
        for c in range(n):
            if sorted(grid[r][c] for r in range(n)) != expected:
                errors.append(f"Kolona {c + 1} nuk përmban 1..{n} nga një herë")
    return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# Hapësira e kërkimit dhe numri i nyjeve në rastin më të keq
# ---------------------------------------------------------------------------

def search_space(n):
    return {
        "naive": n ** (n * n),                  # n^(n²)
        "row_permutations": factorial(n) ** n,  # (n!)^n
        "latin_squares": KNOWN_LATIN_SQUARES.get(n),
        "neighbors": n * (n * (n - 1) // 2),    # fqinjët në landscape: n · C(n, 2)
    }


def worst_case_nodes(n):
    """Numri i nyjeve që viziton IDDFS klasik në pemën pa kufizime
    (b = n, d = n²), nëse zgjidhja është në nivelin e fundit:
        N = Σ_{i=0}^{d} (d + 1 − i) · b^i
    Nyjet e nivelit i vizitohen (d + 1 − i) herë."""
    b, d = n, n * n
    return sum((d + 1 - i) * b ** i for i in range(d + 1))


# ---------------------------------------------------------------------------
# Shfaqja e rezultateve
# ---------------------------------------------------------------------------

def sci(value):
    s = str(value)
    return f"{s[0]}.{s[1:3]}e+{len(s) - 1}" if value >= 10**6 else f"{value:,}"


def print_grid(grid):
    for row in grid:
        print("  " + " ".join(str(x) for x in row))


def main():
    n, step, time_limit = 5, 1, 120
    for arg in sys.argv[1:]:
        if arg.startswith("--step="):
            step = int(arg.split("=", 1)[1])
        elif arg.startswith("--time="):
            time_limit = float(arg.split("=", 1)[1])
        else:
            n = int(arg)
    if n < 1 or step < 1:
        print("n dhe step duhet të jenë numra pozitivë.")
        return

    space = search_space(n)
    print("=" * 66)
    print(f"LATIN SQUARE – IDDFS me Backtracking | n = {n}")
    print("=" * 66)
    print(f"Variabla (qeliza):                {n * n}")
    print(f"Hapësira naive n^(n²):            {sci(space['naive'])}")
    print(f"Permutacione për rresht (n!)^n:   {sci(space['row_permutations'])}")
    if space["latin_squares"]:
        print(f"Katrorë latinë gjithsej L(n):     {sci(space['latin_squares'])}")
    print(f"Hapi i limitit:                   {step}")
    print("-" * 66)

    solver = LatinSquareIDDFS(n, step, time_limit)
    found = solver.iddfs()
    elapsed = time.time() - solver.start_time

    print("Iteracionet e IDDFS:")
    for limit, nodes, result in solver.iterations:
        label = "ZGJIDHJE" if result is True else result
        print(f"  limiti = {limit:3d}   nyje = {nodes:>12,}   -> {label}")
    print("-" * 66)

    if found:
        print("Dalja:")
        print_grid(solver.grid)
        valid, errors = validate_latin_square(solver.grid)
        print("-" * 66)
        print(f"Objective function f(S):          {calculate_objective(solver.grid)}")
        print(f"Katrori latin është i vlefshëm:   {'PO' if valid else 'JO'}")
        for error in errors:
            print("   -", error)
    print(f"Nyje gjithsej (të gjitha iter.):  {solver.nodes:,}")
    print(f"Operacione Backtracking:          {solver.backtracks:,}")
    print(f"Koha e ekzekutimit:               {elapsed:.2f} s")
    reasons = {
        "solution_found": "U gjet zgjidhja.",
        "no_solution": "Nuk ekziston zgjidhje.",
        "time_limit": "Mbaroi koha para se të gjendej zgjidhja.",
    }
    print(f"Arsyeja e ndalimit:               {reasons[solver.stop_reason]}")
    print("=" * 66)


if __name__ == "__main__":
    main()