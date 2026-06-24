import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


TOOL_ROOT = Path(__file__).resolve().parents[1] / "api-tool"
sys.path.insert(0, str(TOOL_ROOT))


class ApiToolCliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_cli_init_add_run_and_scores_without_sync(self):
        from watchdog_koth_api.cli import main

        self.assertEqual(main(["--base", str(self.base), "init"]), 0)
        self.assertEqual(
            main(
                [
                    "--base",
                    str(self.base),
                    "add-run",
                    "--team-id",
                    "1",
                    "--team-name",
                    "Alpha",
                    "--cycles",
                    "0x96",
                    "--no-sync",
                ]
            ),
            0,
        )

        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(main(["--base", str(self.base), "scores"]), 0)

        text = output.getvalue()
        self.assertIn("Alpha", text)
        self.assertIn("150", text)
        self.assertIn("500", text)


class ApiToolWebTests(unittest.TestCase):
    def test_render_dashboard_contains_scores_and_forms(self):
        from watchdog_koth_api.config import Settings
        from watchdog_koth_api.ledger import Run
        from watchdog_koth_api.web import render_dashboard

        html = render_dashboard(
            settings=Settings(),
            runs=[
                Run(
                    run_id=1,
                    team_id=1,
                    team_name="Alpha",
                    cycles=150,
                    created_at="2026-06-24T10:00:00Z",
                )
            ],
            scores={1: {"team_id": 1, "best_cycles": 150, "score": 500}},
            teams=[{"id": 1, "name": "Alpha"}],
            token="secret",
            message="Saved",
        )

        self.assertIn("Watchdog KOTH", html)
        self.assertIn("Alpha", html)
        self.assertIn("Best cycles (hex)", html)
        self.assertIn("Cycles (hex)", html)
        self.assertIn("0x96", html)
        self.assertIn("Delete score", html)
        self.assertIn("Saved", html)

    def test_safe_sync_error_message_redirects_instead_of_raising(self):
        from watchdog_koth_api.web import _sync_message

        def broken_sync():
            raise RuntimeError("ctfd is unhappy")

        message = _sync_message("Run saved", broken_sync)

        self.assertEqual(message, "Run saved; sync failed: ctfd is unhappy")


if __name__ == "__main__":
    unittest.main()
