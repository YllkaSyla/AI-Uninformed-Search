"""
Testet për latin_square_iddfs.py

Ekzekutimi (nga folderi 3-Latin-Square-IDDFS):
    python -m unittest discover tests -v
"""

import os
import sys
import unittest

# Lejon importimin e latin_square_iddfs.py nga folderi prind
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from latin_square_iddfs import (  # noqa: E402
    CUTOFF,
    LatinSquareIDDFS,
    calculate_objective,
    search_space,
    validate_latin_square,
    worst_case_nodes,
)

# Shembulli nga detyra (n = 5)
EXAMPLE = [
    [1, 2, 3, 4, 5],
    [5, 1, 2, 3, 4],
    [4, 5, 1, 2, 3],
    [3, 4, 5, 1, 2],
    [2, 3, 4, 5, 1],
]


class TestObjectiveAndValidation(unittest.TestCase):

    def test_example_from_task_is_valid(self):
        valid, errors = validate_latin_square(EXAMPLE)
        self.assertTrue(valid)
        self.assertEqual(errors, [])
        self.assertEqual(calculate_objective(EXAMPLE), 0)

    def test_repeated_value_in_row(self):
        grid = [[1, 1], [2, 2]]
        self.assertFalse(validate_latin_square(grid)[0])
        self.assertEqual(calculate_objective(grid), 2)     # 1 + 1 përsëritje në rreshta

    def test_repeated_value_in_column(self):
        grid = [[1, 2], [1, 2]]                            # rreshtat në rregull, kolonat jo
        self.assertFalse(validate_latin_square(grid)[0])
        self.assertEqual(calculate_objective(grid), 2)

    def test_wrong_row_length(self):
        self.assertFalse(validate_latin_square([[1, 2], [2]])[0])

    def test_value_outside_domain(self):
        self.assertFalse(validate_latin_square([[1, 3], [3, 1]])[0])


class TestSearchSpace(unittest.TestCase):

    def test_naive_space(self):
        self.assertEqual(search_space(5)["naive"], 5 ** 25)

    def test_row_permutations(self):
        self.assertEqual(search_space(5)["row_permutations"], 120 ** 5)

    def test_neighbors(self):
        self.assertEqual(search_space(5)["neighbors"], 50)      # 5 · C(5,2)

    def test_worst_case_nodes(self):
        # n = 2: b = 2, d = 4 -> 5·1 + 4·2 + 3·4 + 2·8 + 1·16 = 57
        self.assertEqual(worst_case_nodes(2), 57)


class TestIDDFS(unittest.TestCase):

    def solve(self, n, step=1):
        solver = LatinSquareIDDFS(n, step)
        found = solver.iddfs()
        return solver, found

    def test_small_n_are_solved_and_valid(self):
        for n in range(1, 5):
            solver, found = self.solve(n)
            self.assertTrue(found, n)
            self.assertEqual(solver.stop_reason, "solution_found")
            self.assertTrue(validate_latin_square(solver.grid)[0], n)
            self.assertEqual(calculate_objective(solver.grid), 0)

    def test_solution_is_found_at_depth_n_squared(self):
        # Iteracionet 0 .. n²−1 përfundojnë me cutoff; zgjidhja del në limitin n²
        solver, _ = self.solve(4)
        limits = [limit for limit, _, _ in solver.iterations]
        self.assertEqual(limits, list(range(17)))
        self.assertTrue(all(r == CUTOFF for _, _, r in solver.iterations[:-1]))
        self.assertIs(solver.iterations[-1][2], True)

    def test_node_counts_n2(self):
        # Pema për n = 2 ka nyje 1, 2, 2, 2, 2 në nivelet 0..4
        solver, _ = self.solve(2)
        self.assertEqual([nodes for _, nodes, _ in solver.iterations], [1, 3, 5, 7, 5])
        self.assertEqual(solver.nodes, 21)

    def test_first_solution_n5(self):
        solver, found = self.solve(5, step=5)
        self.assertTrue(found)
        self.assertEqual(solver.grid[0], [1, 2, 3, 4, 5])
        self.assertTrue(validate_latin_square(solver.grid)[0])

    def test_step_gives_same_solution(self):
        a, _ = self.solve(4, step=1)
        b, _ = self.solve(4, step=4)
        self.assertEqual(a.grid, b.grid)
        self.assertLess(b.nodes, a.nodes)       # më pak iteracione -> më pak nyje

    def test_backtracking_restores_state(self):
        solver = LatinSquareIDDFS(3)
        solver.assign(0, 0, 1)
        self.assertFalse(solver.is_consistent(0, 1, 1))     # rreshti
        self.assertFalse(solver.is_consistent(1, 0, 1))     # kolona
        solver.backtrack(0, 0, 1)
        self.assertTrue(solver.is_consistent(0, 1, 1))
        self.assertEqual(solver.grid[0][0], 0)
        self.assertEqual(solver.backtracks, 1)

    def test_time_limit(self):
        solver = LatinSquareIDDFS(6, time_limit=0.5)
        self.assertFalse(solver.iddfs())
        self.assertEqual(solver.stop_reason, "time_limit")


if __name__ == "__main__":
    unittest.main()