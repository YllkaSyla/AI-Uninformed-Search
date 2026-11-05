"""
Testet për social_golfers.py

Ekzekutimi (nga folderi Social-Golfers):
    python -m unittest discover tests -v
"""

import os
import sys
import unittest

# Lejon importimin e social_golfers.py nga folderi prind
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from social_golfers import (  # noqa: E402
    SocialGolfersDFS,
    calculate_objective,
    generate_groups,
    group_pairs,
    is_valid_group,
    pair_key,
    search_space,
    upper_bound,
    validate_schedule,
)

# Java 1 e fiksuar për n = 32: (0,1,2,3), (4,5,6,7), ..., (28,29,30,31)
WEEK_1 = [tuple(range(j * 4, j * 4 + 4)) for j in range(8)]


def pairs_of(week):
    return {pair for group in week for pair in group_pairs(group)}


class TestHelpers(unittest.TestCase):
    """Funksionet ndihmëse për çiftet dhe grupet."""

    def test_pair_key_is_ordered(self):
        self.assertEqual(pair_key(5, 2), (2, 5))
        self.assertEqual(pair_key(2, 5), (2, 5))

    def test_group_has_six_pairs(self):
        self.assertEqual(len(group_pairs((0, 1, 2, 3))), 6)       # C(4,2) = 6

    def test_week_uses_48_pairs(self):
        self.assertEqual(len(pairs_of(WEEK_1)), 48)               # 8 · 6 = 48

    def test_invalid_group_is_rejected(self):
        # (0,1) dhe (4,5) janë takuar në javën 1
        self.assertFalse(is_valid_group((0, 1, 4, 5), pairs_of(WEEK_1)))

    def test_valid_group_is_accepted(self):
        self.assertTrue(is_valid_group((0, 4, 8, 12), pairs_of(WEEK_1)))


class TestGenerateGroups(unittest.TestCase):
    """Domeni aktual i grupit të parë në javën 2."""

    def setUp(self):
        self.candidates = list(generate_groups(list(range(32)), pairs_of(WEEK_1), 4))

    def test_every_candidate_contains_smallest_player(self):          # SB2
        self.assertTrue(all(group[0] == 0 for group in self.candidates))

    def test_every_candidate_has_four_sorted_players(self):           # C2, SB1
        self.assertTrue(all(len(g) == 4 and list(g) == sorted(g) for g in self.candidates))

    def test_no_candidate_repeats_a_pair(self):                       # C4
        used = pairs_of(WEEK_1)
        self.assertTrue(all(is_valid_group(g, used) for g in self.candidates))

    def test_number_of_candidates(self):
        # 0 + një lojtar nga secili prej 3 grupeve të ndryshme (nga 7) të javës 1:
        # C(7,3) · 4^3 = 35 · 64 = 2240
        self.assertEqual(len(self.candidates), 2240)


class TestSearchSpaceAndBound(unittest.TestCase):

    def test_number_of_groups(self):
        self.assertEqual(search_space(8, 4)["groups"], 35960)                      # C(32,4)

    def test_number_of_partitions(self):
        self.assertEqual(search_space(8, 4)["partitions"], 59287247761257140625)   # 32!/((4!)^8·8!)

    def test_upper_bound(self):
        self.assertEqual(upper_bound(32, 4), 10)
        self.assertEqual(upper_bound(9, 3), 4)
        self.assertEqual(upper_bound(4, 2), 3)


class TestObjectiveAndValidation(unittest.TestCase):

    def test_objective_of_valid_week(self):
        self.assertEqual(calculate_objective([WEEK_1]), (1, 0))

    def test_objective_counts_repeated_pairs(self):
        # Java 2 përmban (0,1,4,5): çiftet (0,1) dhe (4,5) përsëriten -> V = 2
        week_2 = [(0, 1, 4, 5), (2, 3, 6, 7)] + WEEK_1[2:]
        weeks, repeated = calculate_objective([WEEK_1, week_2])
        self.assertEqual(weeks, 2)
        self.assertGreaterEqual(repeated, 2)

    def test_validation_accepts_valid_schedule(self):
        valid, errors = validate_schedule([WEEK_1], 8, 4)
        self.assertTrue(valid)
        self.assertEqual(errors, [])

    def test_validation_detects_wrong_number_of_groups(self):          # C3
        self.assertFalse(validate_schedule([WEEK_1[:7]], 8, 4)[0])

    def test_validation_detects_wrong_group_size(self):                # C2
        week = [(0, 1, 2)] + WEEK_1[1:] + [(3,)]
        self.assertFalse(validate_schedule([week], 8, 4)[0])

    def test_validation_detects_player_twice_in_week(self):            # C1, C5
        week = [(0, 1, 2, 3), (0, 5, 6, 7)] + WEEK_1[2:]
        self.assertFalse(validate_schedule([week], 8, 4)[0])

    def test_validation_detects_repeated_pair(self):                   # C4
        self.assertFalse(validate_schedule([WEEK_1, WEEK_1], 8, 4)[0])


class TestDFS(unittest.TestCase):
    """DFS në instanca të vogla ku rezultati optimal njihet."""

    def run_solver(self, g, p, time_limit=10):
        solver = SocialGolfersDFS(g, p, time_limit)
        schedule, _ = solver.solve()
        return solver, schedule

    def test_sgp_2_2_reaches_upper_bound(self):
        # 4 lojtarë, 2 grupe me 2: kufiri 3 javë arrihet
        solver, schedule = self.run_solver(2, 2)
        self.assertEqual(len(schedule), 3)
        self.assertEqual(solver.stop_reason, "upper_bound")
        self.assertTrue(validate_schedule(schedule, 2, 2)[0])

    def test_sgp_2_3_exhaustive_search_proves_one_week(self):
        # 6 lojtarë, 2 grupe me 3: kufiri teorik është 2, por java 2 është e pamundur.
        # Kërkimi shterues e dëshmon se maksimumi është 1 javë.
        solver, schedule = self.run_solver(2, 3)
        self.assertEqual(len(schedule), 1)
        self.assertEqual(solver.stop_reason, "exhausted")

    def test_sgp_3_3_reaches_upper_bound(self):
        solver, schedule = self.run_solver(3, 3)
        self.assertEqual(len(schedule), 4)
        self.assertEqual(solver.stop_reason, "upper_bound")
        self.assertTrue(validate_schedule(schedule, 3, 3)[0])

    def test_sgp_8_4_finds_valid_schedule(self):
        # Konfigurimi kryesor me kufi kohe të shkurtër (3 s).
        solver, schedule = self.run_solver(8, 4, time_limit=3)
        self.assertGreaterEqual(len(schedule), 5)
        self.assertLessEqual(len(schedule), upper_bound(32, 4))
        self.assertTrue(validate_schedule(schedule, 8, 4)[0])
        self.assertEqual(calculate_objective(schedule)[1], 0)

    def test_backtracking_restores_state(self):
        solver = SocialGolfersDFS(8, 4)
        solver.add_group((0, 1, 2, 3))
        solver.backtrack()
        self.assertEqual(solver.current_week, [])
        self.assertEqual(solver.placed, set())
        self.assertEqual(solver.used_pairs, set())
        self.assertEqual(solver.backtracks, 1)


if __name__ == "__main__":
    unittest.main()