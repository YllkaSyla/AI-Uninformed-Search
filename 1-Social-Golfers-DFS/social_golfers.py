"""
Social Golfers Problem – Depth-First Search (DFS) me Backtracking
=================================================================

n = g × p lojtarë luajnë një herë në javë, në g grupe me nga p lojtarë.
Kërkesa: asnjë çift lojtarësh nuk luan në të njëjtin grup më shumë se një herë.
Qëllimi: të gjendet numri maksimal i javëve w.

Modeli (shih README.md):
    Variabla      B[t][j] = grupi j në javën t (bashkësi me p lojtarë)
    Domeni        të gjitha grupet me p lojtarë nga P = {0, ..., n-1}
    Kufizimet     C1 – C5 (C4: m(a, b) <= 1 për çdo çift)
    Objektivi     f(S) = numri i javëve të plota, me kusht V(S) = 0

Ekzekutimi:
    python social_golfers.py                 # g=8, p=4, kufiri i kohës 60 s
    python social_golfers.py 8 4 120         # g, p, kufiri i kohës në sekonda
"""

import sys
import time
from itertools import combinations
from math import comb, factorial


# ---------------------------------------------------------------------------
# Funksionet ndihmëse për çiftet dhe grupet
# ---------------------------------------------------------------------------

def pair_key(a, b):
    """Kthen çiftin si tuple të renditur (a, b), me a < b."""
    return (a, b) if a < b else (b, a)


def group_pairs(group):
    """Kthen të gjitha çiftet brenda një grupi. Grupi me 4 lojtarë ka C(4,2) = 6 çifte."""
    return [pair_key(a, b) for a, b in combinations(group, 2)]


def is_valid_group(group, used_pairs):
    """Kufizimi C4: grupi lejohet vetëm nëse asnjë nga çiftet e tij
    nuk është takuar në javët e mëparshme."""
    return all(pair not in used_pairs for pair in group_pairs(group))


def generate_groups(available, used_pairs, p):
    """Gjeneron kandidatët (domenin aktual) për grupin e ardhshëm.

    available  – lista e renditur e lojtarëve që ende nuk janë vendosur këtë javë
    used_pairs – bashkësia e çifteve që janë takuar më parë

    Rregullat:
      1. Përdoren vetëm lojtarë të pavendosur këtë javë            (C1, C5)
      2. Grupi ka saktësisht p lojtarë                              (C2)
      3. Grupi përmban lojtarin më të vogël të pavendosur          (SB2)
      4. Lojtarët në grup janë në rend rritës (tuple)              (SB1)
      5. Asnjë çift nuk është takuar më parë                        (C4)
    """
    first = available[0]
    for rest in combinations(available[1:], p - 1):
        group = (first,) + rest
        if is_valid_group(group, used_pairs):
            yield group


def upper_bound(n, p):
    """Kufiri teorik i sipërm: çdo lojtar ka n-1 partnerë dhe çdo javë
    takon p-1 të rinj, prandaj w <= floor((n-1)/(p-1)).
    NUK garanton se ky numër javësh arrihet."""
    return (n - 1) // (p - 1)


# ---------------------------------------------------------------------------
# Funksioni objektiv dhe validimi
# ---------------------------------------------------------------------------

def count_meetings(schedule):
    """Kthen një dictionary: çifti -> sa herë është takuar, m(a, b)."""
    meetings = {}
    for week in schedule:
        for group in week:
            for pair in group_pairs(group):
                meetings[pair] = meetings.get(pair, 0) + 1
    return meetings


def calculate_objective(schedule):
    """Kthen (f, V):
       f(S) = numri i javëve në orar (vlera që maksimizohet)
       V(S) = sum max(0, m(a,b) - 1) = numri i çifteve të përsëritura (duhet 0)"""
    meetings = count_meetings(schedule)
    repeated = sum(count - 1 for count in meetings.values() if count > 1)
    return len(schedule), repeated


def validate_schedule(schedule, g, p):
    """Validim i pavarur i orarit të plotë, nga fillimi.
    Nuk përdor asnjë strukturë nga kërkimi DFS.
    Kthen (True/False, lista e gabimeve)."""
    n = g * p
    errors = []
    for t, week in enumerate(schedule, start=1):
        if len(week) != g:                                          # C3
            errors.append(f"Java {t}: ka {len(week)} grupe, jo {g}")
        for group in week:
            if len(group) != p or len(set(group)) != p:             # C2
                errors.append(f"Java {t}: grupi {group} nuk ka {p} lojtarë të ndryshëm")
        players = [x for group in week for x in group]
        if sorted(players) != list(range(n)):                       # C1, C5
            errors.append(f"Java {t}: jo çdo lojtar paraqitet saktësisht një herë")
    for pair, count in count_meetings(schedule).items():            # C4
        if count > 1:
            errors.append(f"Çifti {pair} është takuar {count} herë")
    return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# DFS me Backtracking
# ---------------------------------------------------------------------------

class SocialGolfersDFS:
    """Kërkimi DFS. Një nyje e kërkimit = një orar i pjesshëm
    (javët e plota + grupet e vendosura në javën aktuale)."""

    def __init__(self, g, p, time_limit=60):
        self.g, self.p = g, p
        self.n = g * p
        self.time_limit = time_limit
        self.max_weeks = upper_bound(self.n, p)

        # Gjendja e kërkimit
        self.weeks = []            # javët e plota (lista e listave të tuples)
        self.current_week = []     # grupet e vendosura në javën aktuale
        self.placed = set()        # lojtarët e vendosur në javën aktuale
        self.used_pairs = set()    # çiftet e takuara deri tani

        # Rezultati dhe statistikat
        self.best_schedule = []
        self.nodes = 0
        self.backtracks = 0
        self.stop_reason = None
        self.start_time = None

    # --- Zgjerimi i gjendjes dhe kthimi prapa ---------------------------

    def add_group(self, group):
        """Vendos grupin në javën aktuale dhe shënon çiftet e tij si të përdorura."""
        self.current_week.append(group)
        self.placed.update(group)
        self.used_pairs.update(group_pairs(group))

    def backtrack(self):
        """BACKTRACKING: heq grupin e fundit dhe i liron çiftet e tij."""
        group = self.current_week.pop()
        self.placed.difference_update(group)
        self.used_pairs.difference_update(group_pairs(group))
        self.backtracks += 1

    # --- DFS rekursiv ---------------------------------------------------

    def dfs(self):
        """Kthen True kur kërkimi duhet të ndalet (kufiri i sipërm ose koha)."""
        self.nodes += 1

        if time.time() - self.start_time > self.time_limit:
            self.stop_reason = "time_limit"
            return True

        # Java aktuale është e plotë (g grupe) -> kemi një javë të re të vlefshme
        if len(self.current_week) == self.g:
            self.weeks.append(self.current_week)
            if len(self.weeks) > len(self.best_schedule):
                self.best_schedule = [list(week) for week in self.weeks]
            if len(self.weeks) == self.max_weeks:
                self.stop_reason = "upper_bound"       # nuk mund të ketë më shumë javë
                return True

            # Fillon java e ardhshme
            saved_placed = self.placed
            self.current_week, self.placed = [], set()
            if self.dfs():
                return True
            # Kthim në javën e mëparshme (e cila ishte e plotë)
            self.current_week, self.placed = self.weeks.pop(), saved_placed
            return False

        # Gjenerimi i kandidatëve për grupin e ardhshëm
        available = [x for x in range(self.n) if x not in self.placed]
        for group in generate_groups(available, self.used_pairs, self.p):
            self.add_group(group)          # zgjerimi i gjendjes
            if self.dfs():                 # vazhdo më thellë
                return True
            self.backtrack()               # asnjë vazhdim nga ky grup -> kthehu prapa
        return False                       # asnjë kandidat nuk funksionoi

    def solve(self):
        """Fiksohet java 1 (SB3) dhe fillon DFS nga java 2."""
        self.start_time = time.time()
        first_week = [tuple(range(j * self.p, (j + 1) * self.p)) for j in range(self.g)]
        for group in first_week:
            self.add_group(group)
        if not self.dfs():
            self.stop_reason = "exhausted"     # e gjithë pema u kontrollua
        return self.best_schedule, time.time() - self.start_time


# ---------------------------------------------------------------------------
# Hapësira e kërkimit (Search Space)
# ---------------------------------------------------------------------------

def search_space(g, p):
    """Llogarit madhësitë kryesore të hapësirës së kërkimit për një javë."""
    n = g * p
    return {
        "groups": comb(n, p),                                       # C(n, p)
        "partitions": factorial(n) // (factorial(p) ** g * factorial(g)),
        "pairs_total": comb(n, 2),
        "pairs_per_week": g * comb(p, 2),
    }


# ---------------------------------------------------------------------------
# Shfaqja e rezultateve
# ---------------------------------------------------------------------------

def print_schedule(schedule):
    for t, week in enumerate(schedule, start=1):
        groups = "  ".join("(" + ",".join(str(x) for x in group) + ")" for group in week)
        print(f"Java {t:2d}: {groups}")


def main():
    g = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    p = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    time_limit = float(sys.argv[3]) if len(sys.argv) > 3 else 60
    n = g * p

    space = search_space(g, p)
    print("=" * 70)
    print("SOCIAL GOLFERS PROBLEM – DFS me Backtracking")
    print("=" * 70)
    print(f"Numri i lojtarëve (n):           {n}")
    print(f"Numri i grupeve (g):             {g}")
    print(f"Madhësia e grupit (p):           {p}")
    print(f"Kufiri teorik i sipërm:          {upper_bound(n, p)} javë (nuk garantohet)")
    print(f"Grupe të mundshme C({n},{p}):      {space['groups']:,}")
    print(f"Ndarje të mundshme për javë:     {space['partitions']:,}")
    print(f"Kufiri i kohës:                  {time_limit:g} s")
    print("-" * 70)

    solver = SocialGolfersDFS(g, p, time_limit)
    schedule, elapsed = solver.solve()
    weeks, repeated = calculate_objective(schedule)
    valid, errors = validate_schedule(schedule, g, p)

    print(f"Numri i javëve të gjetura:       {weeks}")
    print_schedule(schedule)
    print("-" * 70)
    print(f"Çifte të përsëritura V(S):       {repeated}")
    print(f"Nyje të vizituara:               {solver.nodes:,}")
    print(f"Operacione Backtracking:         {solver.backtracks:,}")
    print(f"Koha e ekzekutimit:              {elapsed:.2f} s")
    print(f"Orari është i vlefshëm:          {'PO' if valid else 'JO'}")
    for error in errors:
        print("   -", error)

    reasons = {
        "upper_bound": "U arrit kufiri teorik i sipërm -> rezultati është optimal.",
        "exhausted": "E gjithë pema u kontrollua -> rezultati është dëshmuar optimal.",
        "time_limit": "Mbaroi koha -> rezultati është më i miri i gjetur, "
                      "por NUK është dëshmuar optimal.",
    }
    print(f"Arsyeja e ndalimit:              {reasons[solver.stop_reason]}")
    print("=" * 70)


if __name__ == "__main__":
    main()