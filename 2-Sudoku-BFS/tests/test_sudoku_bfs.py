"""
Testet për sudoku_bfs.py

Ekzekutimi (nga folderi 2-Sudoku-BFS):
    python -m unittest discover tests -v
"""

import os
import sys
import unittest

# Lejon importimin e sudoku_bfs.py nga folderi prind
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from sudoku_bfs import (  # noqa: E402
    PEERS,
    PUZZLES,
    bfs_solve,
    calculate_objective,
    candidates,
    count_conflicts,
    is_valid_puzzle,
    next_empty_cell,
    search_space,
    validate_solution,
)

MEDIUM_SOLUTION = (
    "534678912"
    "672195348"
    "198342567"
    "859761423"
    "426853791"
    "713924856"
    "961537284"
    "287419635"
    "345286179"
)


class TestModel(unittest.TestCase):
    """Fqinjët, domeni dhe kufizimet."""

    def test_every_cell_has_20_peers(self):
        # 8 në rresht + 8 në kolonë + 4 të tjerë në kuti = 20
        self.assertTrue(all(len(p) == 20 for p in PEERS))

    def test_candidates_of_first_empty_cell(self):
        # Medium, qeliza (0,2): rreshti ka 5,3,7; kolona 8; kutia 6,9,8 -> lejohen 1,2,4
        self.assertEqual(candidates(PUZZLES["medium"], 2), ["1", "2", "4"])

    def test_next_empty_cell_is_row_major(self):
        self.assertEqual(next_empty_cell(PUZZLES["medium"]), 2)
        self.assertEqual(next_empty_cell(MEDIUM_SOLUTION), -1)

    def test_all_puzzles_are_valid(self):
        for level, puzzle in PUZZLES.items():
            self.assertTrue(is_valid_puzzle(puzzle), level)

    def test_invalid_puzzle_is_detected(self):
        bad = "55" + PUZZLES["medium"][2:]          # dy 5-sha në rreshtin e parë
        self.assertFalse(is_valid_puzzle(bad))

    def test_number_of_givens(self):
        self.assertEqual(81 - PUZZLES["easy"].count("0"), 36)
        self.assertEqual(81 - PUZZLES["medium"].count("0"), 30)
        self.assertEqual(81 - PUZZLES["hard"].count("0"), 21)


class TestObjectiveAndValidation(unittest.TestCase):

    def test_objective_of_solution_is_zero(self):
        self.assertEqual(calculate_objective(MEDIUM_SOLUTION), (0, 0))

    def test_conflicts_are_counted(self):
        # Ndërrimi i dy vlerave në rreshtin e parë krijon konflikte në kolona dhe kuti
        swapped = "354678912" + MEDIUM_SOLUTION[9:]
        self.assertGreater(count_conflicts(swapped), 0)

    def test_validation_accepts_solution(self):
        valid, errors = validate_solution(MEDIUM_SOLUTION, PUZZLES["medium"])
        self.assertTrue(valid)
        self.assertEqual(errors, [])

    def test_validation_rejects_incomplete_grid(self):
        self.assertFalse(validate_solution(PUZZLES["medium"], PUZZLES["medium"])[0])

    def test_validation_rejects_wrong_solution(self):
        swapped = "354678912" + MEDIUM_SOLUTION[9:]
        self.assertFalse(validate_solution(swapped, PUZZLES["medium"])[0])

    def test_validation_rejects_changed_given(self):
        # Zgjidhje e vlefshme, por e një puzzle tjetër: numrat e dhënë nuk përputhen
        self.assertFalse(validate_solution(MEDIUM_SOLUTION, PUZZLES["easy"])[0])


class TestSearchSpace(unittest.TestCase):

    def test_naive_space(self):
        self.assertEqual(search_space(PUZZLES["medium"])["naive"], 9 ** 51)

    def test_reduced_space_is_smaller(self):
        for puzzle in PUZZLES.values():
            space = search_space(puzzle)
            self.assertLess(space["reduced"], space["naive"])


class TestBFS(unittest.TestCase):

    def check_level(self, level):
        solutions, stats = bfs_solve(PUZZLES[level])
        self.assertEqual(len(solutions), 1)
        self.assertEqual(stats["stop_reason"], "solution_found")
        self.assertTrue(validate_solution(solutions[0], PUZZLES[level])[0])
        self.assertEqual(calculate_objective(solutions[0]), (0, 0))
        return solutions[0], stats

    def test_easy(self):
        self.check_level("easy")

    def test_medium(self):
        solution, _ = self.check_level("medium")
        self.assertEqual(solution, MEDIUM_SOLUTION)

    def test_hard(self):
        self.check_level("hard")

    def test_easy_and_medium_have_unique_solution(self):
        for level in ("easy", "medium"):
            solutions, stats = bfs_solve(PUZZLES[level], find_all=True)
            self.assertEqual(stats["stop_reason"], "exhausted")
            self.assertEqual(len(solutions), 1, level)

    def test_solved_grid_is_goal(self):
        solutions, stats = bfs_solve(MEDIUM_SOLUTION)
        self.assertEqual(solutions, [MEDIUM_SOLUTION])
        self.assertEqual(stats["generated"], 1)

    def test_unsolvable_puzzle(self):
        # Qeliza (0,2) nuk ka vlerë të lejuar: rreshti 1–8 pa 9, kolona përmban 9
        puzzle = "120345678" + "009000000" + "0" * 63
        solutions, stats = bfs_solve(puzzle)
        self.assertEqual(solutions, [])
        self.assertEqual(stats["stop_reason"], "exhausted")
        self.assertGreaterEqual(stats["dead_ends"], 1)

    def test_invalid_puzzle_is_rejected(self):
        solutions, stats = bfs_solve("55" + PUZZLES["medium"][2:])
        self.assertEqual(solutions, [])
        self.assertEqual(stats["stop_reason"], "invalid_puzzle")


if __name__ == "__main__":
    unittest.main()