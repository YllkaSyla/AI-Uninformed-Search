"""
Testet për pemët e kërkimit (detyra 4)

Ekzekutimi (nga folderi 4-Search-Trees):
    python -m unittest discover tests -v
"""

import os
import sys
import unittest

# Lejon importimin e moduleve nga folderi prind
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import eight_puzzle as ep                # noqa: E402
import missionaries_cannibals as mc      # noqa: E402
import rotating_workforce as rw          # noqa: E402
from search_tree import bfs_solution, build_tree, count_by_status, level_counts  # noqa: E402


class TestEightPuzzle(unittest.TestCase):

    def test_number_of_moves_depends_on_blank_position(self):
        problem = ep.EightPuzzle()
        self.assertEqual(len(problem.expand((1, 2, 3, 4, 0, 5, 6, 7, 8))), 4)   # qendër
        self.assertEqual(len(problem.expand((1, 0, 2, 3, 4, 5, 6, 7, 8))), 3)   # anë
        self.assertEqual(len(problem.expand((0, 1, 2, 3, 4, 5, 6, 7, 8))), 2)   # qoshe

    def test_move_swaps_blank(self):
        children = dict((a, s) for a, s, _ in ep.EightPuzzle().expand(ep.START))
        self.assertEqual(children["Down"], (1, 2, 3, 4, 5, 6, 7, 0, 8))

    def test_tree_depth_2(self):
        root, nodes = build_tree(ep.EightPuzzle(), 2, repeated="path")
        self.assertEqual(len(nodes), 17)                       # 1 + 4 + 12
        self.assertEqual(level_counts(nodes), [1, 4, 12])
        stats = count_by_status(nodes)
        self.assertEqual(stats["goal"], 1)
        self.assertEqual(stats["repeated"], 4)                 # kthimi në rrënjë

    def test_tree_without_repeated_check_grows_faster(self):
        _, none_nodes = build_tree(ep.EightPuzzle(ep.CORNER, goal=None), 6, repeated="none")
        _, path_nodes = build_tree(ep.EightPuzzle(ep.CORNER, goal=None), 6, repeated="path")
        self.assertEqual(level_counts(none_nodes), [1, 2, 6, 16, 48, 128, 384])
        self.assertLess(len(path_nodes), len(none_nodes))

    def test_bfs_solution(self):
        goal, _ = bfs_solution(ep.EightPuzzle())
        self.assertEqual(goal.depth, 2)
        self.assertEqual(goal.path_actions(), ["Down", "Right"])

    def test_solvability(self):
        self.assertTrue(ep.is_solvable(ep.START))
        self.assertFalse(ep.is_solvable((2, 1, 3, 4, 5, 6, 7, 8, 0)))   # dy pllaka të ndërruara

    def test_state_space(self):
        self.assertEqual(ep.state_space_size(), 181440)


class TestMissionariesCannibals(unittest.TestCase):

    def test_safety(self):
        self.assertTrue(mc.is_safe(3, 3))
        self.assertTrue(mc.is_safe(0, 2))          # pa misionarë majtas
        self.assertFalse(mc.is_safe(2, 3))         # 2M < 3C majtas
        self.assertFalse(mc.is_safe(1, 0))         # djathtas 2M < 3C

    def test_initial_moves(self):
        children = mc.MissionariesCannibals().expand((3, 3, 1))
        valid = [a for a, _, invalid in children if not invalid]
        self.assertEqual(len(children), 5)
        self.assertEqual(valid, ["0M1C→", "0M2C→", "1M1C→"])

    def test_shortest_solution_has_11_crossings(self):
        goal, _ = bfs_solution(mc.MissionariesCannibals())
        self.assertEqual(goal.depth, 11)
        for state in goal.path_states():
            self.assertTrue(mc.is_safe(state[0], state[1]))

    def test_tree_counts(self):
        root, nodes = build_tree(mc.MissionariesCannibals(), 20, repeated="graph")
        stats = count_by_status(nodes)
        self.assertEqual(len(nodes), 49)
        self.assertEqual(stats["goal"], 2)
        self.assertEqual(stats["invalid"], 18)

    def test_repeated_state_handling_reduces_tree(self):
        _, none_nodes = build_tree(mc.MissionariesCannibals(), 11, repeated="none")
        _, path_nodes = build_tree(mc.MissionariesCannibals(), 11, repeated="path")
        self.assertEqual(len(none_nodes), 30641)
        self.assertEqual(len(path_nodes), 91)


class TestRotatingWorkforce(unittest.TestCase):

    def test_forbidden_sequence(self):
        self.assertEqual(rw.partial_violation(("N", "D")), "D pas N")
        self.assertIsNone(rw.partial_violation(("D", "N")))

    def test_block_limits(self):
        self.assertEqual(rw.partial_violation(("-", "-", "-")), "pushim > 2")
        self.assertEqual(rw.partial_violation(("D", "D", "D", "D", "D")), "bllok pune > 4")
        self.assertEqual(rw.partial_violation(("-", "D", "-")), "bllok pune < 2")
        self.assertIsNone(rw.partial_violation(("D", "-")))   # blloku i parë mund të vazhdojë ciklikisht

    def test_daily_demand(self):
        # Rreshti 1 e hëna = D, rreshti 2 e hëna = D -> tepër D të hënën
        schedule = ("D", "D", "-", "D", "D", "-", "-", "D")
        self.assertEqual(rw.partial_violation(schedule), "tepër D të Hë")

    def test_tree_depth_3(self):
        _, nodes = build_tree(rw.RotatingWorkforce(), 3, repeated="none")
        stats = count_by_status(nodes)
        self.assertEqual(len(nodes), 37)
        self.assertEqual(stats["invalid"], 7)

    def test_full_tree_and_solution(self):
        solution, count, levels = rw.dfs_count(rw.RotatingWorkforce(), find_first=False)
        self.assertEqual(count, 885)
        self.assertEqual(sum(levels), 35082)
        self.assertTrue(rw.validate_schedule(solution)[0])

    def test_validation_detects_errors(self):
        bad = ("D",) * rw.LENGTH
        valid, errors = rw.validate_schedule(bad)
        self.assertFalse(valid)
        self.assertGreater(len(errors), 0)


if __name__ == "__main__":
    unittest.main()