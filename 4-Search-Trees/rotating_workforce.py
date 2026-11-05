"""
Rotating Workforce Scheduling – Pema e kërkimit (Search Tree)
=============================================================

Një orar ciklik për n punonjës dhe 7 ditë: punonjësi i në javën e ardhshme
merr rreshtin i+1 të orarit, dhe punonjësi i fundit merr rreshtin e parë.
Kështu i gjithë orari lexohet si një varg i vetëm ciklik me 7·n ditë.

Instanca e këtij projekti (e vogël, që pema të mund të vizatohet):
    Punonjës (rreshta):     3
    Ndërrimet:              D (ditë), N (natë), - (pushim)
    Nevoja për çdo ditë:    1 D dhe 1 N  (pra 1 punonjës pushon)
    Blloqe pune:            2 deri 4 ditë rresht
    Blloqe pushimi:         1 deri 2 ditë rresht
    Vargu i ndaluar:        D menjëherë pas N-së nuk lejohet ("N D"),
                            sepse pas ndërrimit të natës nuk fillohet ndërrimi i ditës

Formulimi (shih README.md):
    Gjendja       orari i pjesshëm: vargu i ndërrimeve të caktuara,
                  qelizë pas qelize (rreshti 1 e hëna, rreshti 1 e marta, ...)
    Fillestare    orari bosh
    Veprimet      cakto D, N ose - në qelizën e ardhshme
    Qëllimi       të gjitha 7·n qelizat të caktuara dhe të gjitha kufizimet të plotësuara

Ekzekutimi:
    python rotating_workforce.py              # pema deri në thellësinë 3
    python rotating_workforce.py 4            # pema deri në thellësinë 4
    python rotating_workforce.py 3 --mermaid  # edhe kodi Mermaid për README
"""

import sys

from search_tree import build_tree, count_by_status, level_counts, print_tree, to_mermaid

EMPLOYEES = 3
DAYS = 7
SHIFTS = ["D", "N", "-"]
DEMAND = {"D": 1, "N": 1, "-": EMPLOYEES - 2}      # për çdo ditë
WORK_MIN, WORK_MAX = 2, 4
OFF_MIN, OFF_MAX = 1, 2
FORBIDDEN = [("N", "D")]                           # D menjëherë pas N-së
DAY_NAMES = ["Hë", "Ma", "Më", "En", "Pr", "Sh", "Di"]
LENGTH = EMPLOYEES * DAYS


def is_work(shift):
    return shift != "-"


def partial_violation(schedule):
    """Kontrollon vetëm qelizën e fundit të vendosur, kundrejt kufizimeve
    që mund të verifikohen në orarin e pjesshëm. Kthen arsyen ose None."""
    i = len(schedule) - 1
    shift = schedule[i]
    day = i % DAYS

    # K1: nevoja ditore nuk tejkalohet
    used = sum(1 for k in range(day, i + 1, DAYS) if schedule[k] == shift)
    if used > DEMAND[shift]:
        return f"tepër {shift} të {DAY_NAMES[day]}"

    if i > 0:
        prev = schedule[i - 1]
        # K4: vargu i ndaluar
        if (prev, shift) in FORBIDDEN:
            return f"{shift} pas {prev}"

    # K2, K3: gjatësia e bllokut aktual (pune ose pushimi)
    run = 1
    while run <= i and is_work(schedule[i - run]) == is_work(shift):
        run += 1
    limit = WORK_MAX if is_work(shift) else OFF_MAX
    if run > limit:
        return "bllok pune > " + str(WORK_MAX) if is_work(shift) else "pushim > " + str(OFF_MAX)

    # Blloku që sapo u mbyll duhet të ketë gjatësinë minimale
    # (përveç bllokut të parë, sepse ai mund të vazhdojë nga fundi i orarit ciklik)
    if i > 0 and is_work(schedule[i - 1]) != is_work(shift):
        end = i - 1
        length = 1
        while end - length >= 0 and is_work(schedule[end - length]) == is_work(schedule[end]):
            length += 1
        starts_at_zero = end - length + 1 == 0
        minimum = WORK_MIN if is_work(schedule[end]) else OFF_MIN
        if length < minimum and not starts_at_zero:
            return "bllok pune < " + str(WORK_MIN) if is_work(schedule[end]) else "pushim < " + str(OFF_MIN)
    return None


def validate_schedule(schedule):
    """Validim i pavarur i orarit të plotë ciklik. Kthen (True/False, gabimet)."""
    errors = []
    if len(schedule) != LENGTH:
        return False, [f"Orari ka {len(schedule)} qeliza, jo {LENGTH}"]
    for day in range(DAYS):                                         # K1
        column = [schedule[e * DAYS + day] for e in range(EMPLOYEES)]
        for shift, need in DEMAND.items():
            if column.count(shift) != need:
                errors.append(f"{DAY_NAMES[day]}: {column.count(shift)} {shift}, duhen {need}")
    for k in range(LENGTH):                                         # K4 (ciklik)
        if (schedule[k], schedule[(k + 1) % LENGTH]) in FORBIDDEN:
            errors.append(f"Vargu i ndaluar në pozitat {k}–{(k + 1) % LENGTH}")
    # K2, K3: blloqet ciklike
    if all(is_work(s) for s in schedule) or not any(is_work(s) for s in schedule):
        errors.append("Orari nuk ka blloqe pune dhe pushimi")
        return False, errors
    start = next(k for k in range(LENGTH) if is_work(schedule[k]) != is_work(schedule[k - 1]))
    k = start
    for _ in range(LENGTH):
        if is_work(schedule[k % LENGTH]) != is_work(schedule[(k - 1) % LENGTH]):
            length = 1
            while is_work(schedule[(k + length) % LENGTH]) == is_work(schedule[k % LENGTH]):
                length += 1
            work = is_work(schedule[k % LENGTH])
            low, high = (WORK_MIN, WORK_MAX) if work else (OFF_MIN, OFF_MAX)
            if not low <= length <= high:
                errors.append(f"Bllok {'pune' if work else 'pushimi'} me gjatësi {length}")
        k += 1
    return len(errors) == 0, errors


class RotatingWorkforce:
    initial = ()

    def goal_test(self, state):
        return len(state) == LENGTH and validate_schedule(state)[0]

    def expand(self, state):
        if len(state) == LENGTH:
            return []
        cell = len(state)
        children = []
        for shift in SHIFTS:
            child = state + (shift,)
            action = f"E{cell // DAYS + 1}-{DAY_NAMES[cell % DAYS]}={shift}"
            children.append((action, child, partial_violation(child)))
        return children

    def format(self, state):
        if not state:
            return "[bosh]"
        rows = ["".join(state[r:r + DAYS]) for r in range(0, len(state), DAYS)]
        return " / ".join(rows)


def dfs_count(problem, find_first=True):
    """DFS me backtracking mbi pemën e kërkimit. Kthen (zgjidhja e parë,
    numri i zgjidhjeve, nyjet në çdo nivel)."""
    levels = [0] * (LENGTH + 1)
    solutions = []

    def dfs(state):
        levels[len(state)] += 1
        if len(state) == LENGTH:
            if validate_schedule(state)[0]:
                solutions.append(state)
                return find_first
            return False
        for _, child, invalid in problem.expand(state):
            if not invalid and dfs(child):
                return True
        return False

    dfs(problem.initial)
    return (solutions[0] if solutions else None), len(solutions), levels


def print_schedule(schedule):
    print("       " + "  ".join(DAY_NAMES))
    for e in range(EMPLOYEES):
        row = schedule[e * DAYS:(e + 1) * DAYS]
        print(f"  E{e + 1}:  " + "   ".join(row))


def main():
    depth = 3
    mermaid = "--mermaid" in sys.argv
    for arg in sys.argv[1:]:
        if arg.isdigit():
            depth = int(arg)

    problem = RotatingWorkforce()
    print("=" * 70)
    print("ROTATING WORKFORCE SCHEDULING – Pema e kërkimit")
    print("=" * 70)
    print(f"Punonjës: {EMPLOYEES} | Ditë: {DAYS} | Qeliza (thellësia e pemës): {LENGTH}")
    print(f"Nevoja ditore: {DEMAND['D']} D, {DEMAND['N']} N, {DEMAND['-']} pushim")
    print(f"Blloqe pune {WORK_MIN}–{WORK_MAX} | pushimi {OFF_MIN}–{OFF_MAX} | e ndaluar: D pas N")
    print(f"Hapësira naive 3^{LENGTH}:   {3 ** LENGTH:,}")
    print("-" * 70)

    root, nodes = build_tree(problem, depth, repeated="none")
    print(print_tree(root, problem))
    stats = count_by_status(nodes)
    print(f"Nyje deri në thellësinë {depth}: {len(nodes)} "
          f"(të vlefshme: {stats['valid']}, të pavlefshme: {stats['invalid']})")
    print("-" * 70)

    solution, count, levels = dfs_count(problem, find_first=False)
    print(f"Pema e plotë (DFS me backtracking, vetëm nyjet e vlefshme):")
    print(f"  Nyje në çdo nivel: {levels}")
    print(f"  Nyje gjithsej:     {sum(levels):,}")
    print(f"  Zgjidhje (orare të vlefshme): {count}")
    if solution:
        print("Zgjidhja e parë:")
        print_schedule(solution)
        print(f"  E vlefshme: {'PO' if validate_schedule(solution)[0] else 'JO'}")
    if mermaid:
        print("-" * 70)
        print(to_mermaid(root, problem))
    print("=" * 70)


if __name__ == "__main__":
    main()