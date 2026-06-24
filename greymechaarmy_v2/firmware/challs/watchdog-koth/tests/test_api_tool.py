import csv
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path


TOOL_ROOT = Path(__file__).resolve().parents[1] / "api-tool"
sys.path.insert(0, str(TOOL_ROOT))


class ApiToolLedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_init_creates_default_files(self):
        from watchdog_koth_api.config import load_settings
        from watchdog_koth_api.ledger import init_storage, load_runs
        from watchdog_koth_api.state import load_state

        init_storage(self.base)

        self.assertTrue((self.base / "settings.json").exists())
        self.assertTrue((self.base / "runs.csv").exists())
        self.assertTrue((self.base / "sync_state.json").exists())
        self.assertEqual(load_runs(self.base / "runs.csv"), [])
        self.assertEqual(load_settings(self.base / "settings.json").challenge_name, "Watchdog KOTH")
        self.assertEqual(load_state(self.base / "sync_state.json").challenge_id, None)

    def test_csv_ledger_supports_decimal_hex_void_and_delete_score(self):
        from watchdog_koth_api.ledger import (
            add_run,
            delete_score,
            init_storage,
            load_runs,
            void_run,
        )
        from watchdog_koth_api.scoring import compute_scores

        init_storage(self.base)
        first = add_run(
            self.base / "runs.csv",
            team_id=1,
            team_name="Alpha",
            cycles="0x96",
            note="hex",
            created_by="admin",
            now="2026-06-24T10:00:00Z",
        )
        second = add_run(
            self.base / "runs.csv",
            team_id=2,
            team_name="Beta",
            cycles="300",
            note="decimal",
            created_by="admin",
            now="2026-06-24T10:01:00Z",
        )

        scores = compute_scores(load_runs(self.base / "runs.csv"), 500, 1)
        self.assertEqual(first.run_id, 1)
        self.assertEqual(second.run_id, 2)
        self.assertEqual(scores[1]["best_cycles"], 150)
        self.assertEqual(scores[1]["score"], 500)
        self.assertEqual(scores[2]["score"], 250)

        void_run(
            self.base / "runs.csv",
            run_id=first.run_id,
            reason="bad measurement",
            now="2026-06-24T10:02:00Z",
        )
        scores = compute_scores(load_runs(self.base / "runs.csv"), 500, 1)
        self.assertNotIn(1, scores)
        self.assertEqual(scores[2]["score"], 500)

        delete_score(
            self.base / "runs.csv",
            team_id=2,
            reason="clear team",
            now="2026-06-24T10:03:00Z",
        )
        self.assertEqual(compute_scores(load_runs(self.base / "runs.csv"), 500, 1), {})

    def test_import_csv_appends_valid_rows(self):
        from watchdog_koth_api.ledger import import_runs, init_storage, load_runs

        init_storage(self.base)
        incoming = self.base / "incoming.csv"
        with incoming.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["team_id", "team_name", "cycles", "note", "created_by"],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "team_id": "7",
                    "team_name": "Gamma",
                    "cycles": "0x40",
                    "note": "imported",
                    "created_by": "sheet",
                }
            )

        imported = import_runs(
            self.base / "runs.csv",
            incoming,
            now="2026-06-24T10:04:00Z",
        )

        self.assertEqual(imported, 1)
        runs = load_runs(self.base / "runs.csv")
        self.assertEqual(runs[0].team_id, 7)
        self.assertEqual(runs[0].cycles, 64)


class FakeCtfdClient:
    def __init__(self):
        self.challenge = None
        self.next_challenge_id = 100
        self.next_award_id = 200
        self.next_submission_id = 300
        self.deleted_awards = []
        self.deleted_submissions = []
        self.created_awards = []
        self.created_submissions = []
        self.promoted = []
        self.team_solves = {}
        self.team_awards = {}
        self.teams = [
            {"id": 1, "name": "Alpha"},
            {"id": 2, "name": "Beta"},
        ]
        self.members = {
            1: [{"id": 11, "name": "alpha-user"}],
            2: [{"id": 22, "name": "beta-user"}],
        }

    def list_challenges(self):
        return [] if self.challenge is None else [self.challenge]

    def create_challenge(self, payload):
        self.challenge = dict(payload)
        self.challenge["id"] = self.next_challenge_id
        return self.challenge

    def update_challenge(self, challenge_id, payload):
        self.challenge.update(payload)
        self.challenge["id"] = challenge_id
        return self.challenge

    def list_teams(self):
        return list(self.teams)

    def list_team_members(self, team_id):
        return list(self.members.get(team_id, []))

    def list_team_solves(self, team_id):
        return list(self.team_solves.get(team_id, []))

    def list_team_awards(self, team_id):
        return list(self.team_awards.get(team_id, []))

    def get_award(self, award_id):
        if award_id in self.deleted_awards:
            return None
        for awards in self.team_awards.values():
            for award in awards:
                if award.get("id") == award_id:
                    return award
        return {"id": award_id}

    def create_award(self, payload):
        award = dict(payload)
        award["id"] = self.next_award_id
        self.next_award_id += 1
        self.created_awards.append(award)
        self.team_awards.setdefault(int(award["team_id"]), []).append(award)
        return award

    def delete_award(self, award_id):
        self.deleted_awards.append(award_id)
        for team_id, awards in list(self.team_awards.items()):
            self.team_awards[team_id] = [
                award for award in awards if award.get("id") != award_id
            ]

    def get_submission(self, submission_id):
        if submission_id in self.deleted_submissions:
            return None
        return {"id": submission_id}

    def create_submission(self, payload):
        submission = dict(payload)
        submission["id"] = self.next_submission_id
        self.next_submission_id += 1
        self.created_submissions.append(submission)
        return submission

    def promote_submission_to_solve(self, submission_id):
        self.promoted.append(submission_id)
        return {"id": submission_id, "type": "correct"}

    def delete_submission(self, submission_id):
        self.deleted_submissions.append(submission_id)


class ApiToolSyncTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_sync_creates_challenge_awards_and_solves(self):
        from watchdog_koth_api.config import load_settings, save_settings
        from watchdog_koth_api.ledger import add_run, init_storage, load_runs
        from watchdog_koth_api.state import load_state, save_state
        from watchdog_koth_api.sync import sync_scores

        init_storage(self.base)
        add_run(self.base / "runs.csv", 1, "Alpha", "100", now="2026-06-24T10:00:00Z")
        add_run(self.base / "runs.csv", 2, "Beta", "200", now="2026-06-24T10:00:01Z")

        client = FakeCtfdClient()
        settings = load_settings(self.base / "settings.json")
        state = load_state(self.base / "sync_state.json")

        summary = sync_scores(client, settings, state, load_runs(self.base / "runs.csv"))
        save_state(self.base / "sync_state.json", state)
        save_settings(self.base / "settings.json", settings)

        self.assertEqual(summary["scored_teams"], 2)
        self.assertEqual(client.challenge["value"], 0)
        self.assertEqual(len(client.created_awards), 2)
        self.assertEqual(len(client.created_submissions), 2)
        self.assertEqual(client.promoted, [300, 301])
        reloaded = json.loads((self.base / "sync_state.json").read_text())
        self.assertEqual(reloaded["challenge_id"], 100)
        self.assertEqual(reloaded["teams"]["1"]["last_score"], 500)
        self.assertEqual(reloaded["teams"]["2"]["last_score"], 250)

    def test_sync_recreates_changed_award_and_deletes_stale_team_artifacts(self):
        from watchdog_koth_api.config import load_settings
        from watchdog_koth_api.ledger import add_run, delete_score, init_storage, load_runs
        from watchdog_koth_api.state import load_state
        from watchdog_koth_api.sync import sync_scores

        init_storage(self.base)
        add_run(self.base / "runs.csv", 1, "Alpha", "100", now="2026-06-24T10:00:00Z")
        add_run(self.base / "runs.csv", 2, "Beta", "400", now="2026-06-24T10:00:01Z")
        client = FakeCtfdClient()
        settings = load_settings(self.base / "settings.json")
        state = load_state(self.base / "sync_state.json")

        sync_scores(client, settings, state, load_runs(self.base / "runs.csv"))
        beta_award_id = state.teams["2"].award_id
        beta_solve_id = state.teams["2"].solve_id

        add_run(self.base / "runs.csv", 2, "Beta", "200", now="2026-06-24T10:01:00Z")
        sync_scores(client, settings, state, load_runs(self.base / "runs.csv"))
        self.assertIn(beta_award_id, client.deleted_awards)
        self.assertNotEqual(state.teams["2"].award_id, beta_award_id)
        self.assertEqual(state.teams["2"].last_score, 250)

        delete_score(self.base / "runs.csv", 2, "clear", now="2026-06-24T10:02:00Z")
        sync_scores(client, settings, state, load_runs(self.base / "runs.csv"))
        self.assertIn(state.teams["2"].award_id, [None])
        self.assertIn(beta_solve_id, client.deleted_submissions)

    def test_sync_recovers_existing_solve_when_state_is_missing(self):
        from watchdog_koth_api.config import load_settings
        from watchdog_koth_api.ledger import add_run, init_storage, load_runs
        from watchdog_koth_api.state import load_state
        from watchdog_koth_api.sync import sync_scores

        init_storage(self.base)
        add_run(self.base / "runs.csv", 1, "Alpha", "100", now="2026-06-24T10:00:00Z")
        client = FakeCtfdClient()
        settings = load_settings(self.base / "settings.json")
        state = load_state(self.base / "sync_state.json")
        client.challenge = {"id": 100, "name": settings.challenge_name}
        client.team_solves[1] = [
            {
                "id": 777,
                "challenge_id": 100,
                "challenge": {"id": 100, "name": settings.challenge_name},
            }
        ]

        sync_scores(client, settings, state, load_runs(self.base / "runs.csv"))

        self.assertEqual(state.teams["1"].solve_id, 777)
        self.assertEqual(client.created_submissions, [])

    def test_sync_recovers_existing_award_when_state_is_missing(self):
        from watchdog_koth_api.config import load_settings
        from watchdog_koth_api.ledger import add_run, init_storage, load_runs
        from watchdog_koth_api.state import load_state
        from watchdog_koth_api.sync import sync_scores

        init_storage(self.base)
        add_run(self.base / "runs.csv", 1, "Alpha", "100", now="2026-06-24T10:00:00Z")
        client = FakeCtfdClient()
        settings = load_settings(self.base / "settings.json")
        state = load_state(self.base / "sync_state.json")
        client.challenge = {"id": 100, "name": settings.challenge_name}
        client.team_awards[1] = [
            {
                "id": 888,
                "team_id": 1,
                "user_id": 11,
                "name": settings.award_name,
                "category": "watchdog-koth",
                "value": 500,
                "description": "Best watchdog run: 100 cycles",
            }
        ]

        sync_scores(client, settings, state, load_runs(self.base / "runs.csv"))

        self.assertEqual(state.teams["1"].award_id, 888)
        self.assertEqual(client.created_awards, [])

    def test_sync_replaces_existing_award_instead_of_adding_duplicate(self):
        from watchdog_koth_api.config import load_settings
        from watchdog_koth_api.ledger import add_run, init_storage, load_runs
        from watchdog_koth_api.state import load_state
        from watchdog_koth_api.sync import sync_scores

        init_storage(self.base)
        add_run(self.base / "runs.csv", 1, "Alpha", "100", now="2026-06-24T10:00:00Z")
        add_run(self.base / "runs.csv", 2, "Beta", "200", now="2026-06-24T10:00:01Z")
        client = FakeCtfdClient()
        settings = load_settings(self.base / "settings.json")
        state = load_state(self.base / "sync_state.json")
        client.challenge = {"id": 100, "name": settings.challenge_name}
        client.team_awards[2] = [
            {
                "id": 889,
                "team_id": 2,
                "user_id": 22,
                "name": settings.award_name,
                "category": "watchdog-koth",
                "value": 400,
                "description": "stale",
            }
        ]

        sync_scores(client, settings, state, load_runs(self.base / "runs.csv"))

        self.assertIn(889, client.deleted_awards)
        self.assertEqual(len(client.team_awards[2]), 1)
        self.assertEqual(client.team_awards[2][0]["value"], 250)
        self.assertNotEqual(client.team_awards[2][0]["id"], 889)


if __name__ == "__main__":
    unittest.main()
