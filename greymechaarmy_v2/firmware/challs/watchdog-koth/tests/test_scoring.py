import os
import sys
import unittest


PLUGIN_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "ctfd-plugin")
)
sys.path.insert(0, PLUGIN_ROOT)


class ScoringTests(unittest.TestCase):
    def test_rejects_non_positive_cycles(self):
        from watchdog_koth.scoring import validate_cycles

        with self.assertRaises(ValueError):
            validate_cycles(0)
        with self.assertRaises(ValueError):
            validate_cycles(-1)

    def test_valid_cycles_are_integerized(self):
        from watchdog_koth.scoring import validate_cycles

        self.assertEqual(validate_cycles("12345"), 12345)
        self.assertEqual(validate_cycles("096"), 96)

    def test_hex_cycles_are_supported_with_prefix(self):
        from watchdog_koth.scoring import validate_cycles

        self.assertEqual(validate_cycles("0x96"), 150)
        self.assertEqual(validate_cycles("0X64"), 100)

    def test_invalid_hex_cycles_are_rejected(self):
        from watchdog_koth.scoring import validate_cycles

        with self.assertRaises(ValueError):
            validate_cycles("0xnot-a-cycle-count")

    def test_no_runs_return_no_scores(self):
        from watchdog_koth.scoring import compute_scores

        self.assertEqual(compute_scores([], max_points=500, min_points=1), {})

    def test_fastest_ratio_scores_best_and_slower_teams(self):
        from watchdog_koth.scoring import compute_scores

        runs = [
            {"team_id": 1, "run_id": 10, "cycles": 100},
            {"team_id": 2, "run_id": 20, "cycles": 250},
        ]

        scores = compute_scores(runs, max_points=500, min_points=1)

        self.assertEqual(scores[1]["best_cycles"], 100)
        self.assertEqual(scores[1]["score"], 500)
        self.assertEqual(scores[2]["best_cycles"], 250)
        self.assertEqual(scores[2]["score"], 200)

    def test_best_valid_run_per_team_wins(self):
        from watchdog_koth.scoring import compute_scores

        runs = [
            {"team_id": 1, "run_id": 10, "cycles": 300},
            {"team_id": 1, "run_id": 11, "cycles": 120},
            {"team_id": 2, "run_id": 20, "cycles": 240},
        ]

        scores = compute_scores(runs, max_points=500, min_points=1)

        self.assertEqual(scores[1]["best_run_id"], 11)
        self.assertEqual(scores[1]["best_cycles"], 120)
        self.assertEqual(scores[1]["score"], 500)
        self.assertEqual(scores[2]["score"], 250)

    def test_ties_share_score(self):
        from watchdog_koth.scoring import compute_scores

        runs = [
            {"team_id": 1, "run_id": 10, "cycles": 100},
            {"team_id": 2, "run_id": 20, "cycles": 100},
        ]

        scores = compute_scores(runs, max_points=500, min_points=1)

        self.assertEqual(scores[1]["score"], 500)
        self.assertEqual(scores[2]["score"], 500)

    def test_voided_runs_are_ignored(self):
        from watchdog_koth.scoring import compute_scores

        runs = [
            {"team_id": 1, "run_id": 10, "cycles": 100, "voided": True},
            {"team_id": 1, "run_id": 11, "cycles": 200},
            {"team_id": 2, "run_id": 20, "cycles": 400},
        ]

        scores = compute_scores(runs, max_points=500, min_points=1)

        self.assertEqual(scores[1]["best_run_id"], 11)
        self.assertEqual(scores[1]["score"], 500)
        self.assertEqual(scores[2]["score"], 250)

    def test_scores_clamp_to_minimum(self):
        from watchdog_koth.scoring import compute_scores

        runs = [
            {"team_id": 1, "run_id": 10, "cycles": 100},
            {"team_id": 2, "run_id": 20, "cycles": 100000},
        ]

        scores = compute_scores(runs, max_points=500, min_points=10)

        self.assertEqual(scores[2]["score"], 10)

    def test_object_runs_can_use_id_field(self):
        from watchdog_koth.scoring import compute_scores

        class Run(object):
            def __init__(self, run_id, team_id, cycles):
                self.id = run_id
                self.team_id = team_id
                self.cycles = cycles
                self.voided_at = None

        scores = compute_scores(
            [Run(run_id=123, team_id=1, cycles=100)],
            max_points=500,
            min_points=1,
        )

        self.assertEqual(scores[1]["best_run_id"], 123)


if __name__ == "__main__":
    unittest.main()
