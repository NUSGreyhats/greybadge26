from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse

from .config import DEFAULT_RUNS_FILE, DEFAULT_SETTINGS_FILE, DEFAULT_STATE_FILE, load_settings
from .ctfd_client import CtfdClient
from .ledger import add_run, delete_score, load_runs, void_run
from .scoring import compute_scores
from .state import load_state, save_state
from .sync import sync_scores


def _token_query(token):
    return urlencode({"token": token})


def render_dashboard(settings, runs, scores, teams, token, message=""):
    team_options = []
    known = {int(team["id"]): team.get("name", "") for team in teams}
    for run in runs:
        known.setdefault(run.team_id, run.team_name)
    for team_id in sorted(known):
        team_options.append(
            '<option value="{0}">{0} - {1}</option>'.format(
                team_id,
                escape(known[team_id]),
            )
        )

    rows = []
    for team_id in sorted(known):
        score = scores.get(team_id)
        rows.append(
            "<tr><td>{team_id}</td><td>{name}</td><td>{cycles}</td><td>{score}</td>"
            "<td><form method='post' action='/delete-score'><input type='hidden' name='token' value='{token}'>"
            "<input type='hidden' name='team_id' value='{team_id}'><button>Delete score</button></form></td></tr>".format(
                team_id=team_id,
                name=escape(known[team_id]),
                cycles="" if score is None else score["best_cycles"],
                score="" if score is None else score["score"],
                token=escape(token),
            )
        )

    run_rows = []
    for run in sorted(runs, key=lambda item: item.run_id, reverse=True)[:50]:
        run_rows.append(
            "<tr><td>{id}</td><td>{team}</td><td>{cycles}</td><td>{note}</td><td>{voided}</td>"
            "<td><form method='post' action='/void-run'><input type='hidden' name='token' value='{token}'>"
            "<input type='hidden' name='run_id' value='{id}'><button>Void</button></form></td></tr>".format(
                id=run.run_id,
                team=escape(run.team_name or str(run.team_id)),
                cycles=run.cycles,
                note=escape(run.note),
                voided=escape(run.voided_at),
                token=escape(token),
            )
        )

    return """<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Watchdog KOTH</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #17202a; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1rem 0 2rem; }}
    th, td {{ border: 1px solid #d5dde5; padding: 0.45rem 0.6rem; text-align: left; }}
    input, select, button {{ margin: 0.2rem; padding: 0.35rem 0.45rem; }}
    .message {{ background: #eef8f1; border: 1px solid #b7dfc2; padding: 0.7rem; }}
  </style>
</head>
<body>
  <h1>Watchdog KOTH</h1>
  {message}
  <form method="post" action="/add-run">
    <input type="hidden" name="token" value="{token}">
    <select name="team_id">{team_options}</select>
    <input name="cycles" placeholder="Cycles, e.g. 150 or 0x96" required>
    <input name="note" placeholder="Note">
    <button>Add run</button>
  </form>
  <form method="post" action="/sync">
    <input type="hidden" name="token" value="{token}">
    <button>Resync all</button>
  </form>
  <h2>Scores</h2>
  <table><tr><th>Team ID</th><th>Team</th><th>Best cycles</th><th>Score</th><th>Actions</th></tr>{rows}</table>
  <h2>Runs</h2>
  <table><tr><th>Run ID</th><th>Team</th><th>Cycles</th><th>Note</th><th>Voided</th><th>Actions</th></tr>{run_rows}</table>
  <p>Example hex input: 0x96</p>
</body>
</html>
""".format(
        message="" if not message else '<div class="message">{0}</div>'.format(escape(message)),
        token=escape(token),
        team_options="".join(team_options),
        rows="".join(rows),
        run_rows="".join(run_rows),
    )


def _paths(base):
    base = Path(base)
    return {
        "settings": base / DEFAULT_SETTINGS_FILE,
        "runs": base / DEFAULT_RUNS_FILE,
        "state": base / DEFAULT_STATE_FILE,
    }


def _teams(settings):
    try:
        return CtfdClient(settings.ctfd_url, settings.ctfd_token).list_teams()
    except Exception:
        return []


def _sync(paths, settings):
    state = load_state(paths["state"])
    summary = sync_scores(
        CtfdClient(settings.ctfd_url, settings.ctfd_token),
        settings,
        state,
        load_runs(paths["runs"]),
    )
    save_state(paths["state"], state)
    return summary


def _sync_message(success_message, sync_func):
    try:
        sync_func()
        return success_message
    except Exception as exc:
        return "{0}; sync failed: {1}".format(success_message, exc)


class WatchdogHandler(BaseHTTPRequestHandler):
    base = Path(".")

    def _settings(self):
        return load_settings(_paths(self.base)["settings"])

    def _authorized(self, params):
        return params.get("token", [""])[0] == self._settings().web_token

    def _send(self, status, body, content_type="text/html; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def _redirect(self, token, message):
        self.send_response(303)
        self.send_header("Location", "/?{0}&message={1}".format(_token_query(token), urlencode({"": message})[1:]))
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        if not self._authorized(params):
            self._send(403, "Forbidden", "text/plain; charset=utf-8")
            return
        paths = _paths(self.base)
        settings = self._settings()
        runs = load_runs(paths["runs"])
        html = render_dashboard(
            settings=settings,
            runs=runs,
            scores=compute_scores(runs, settings.max_points, settings.min_points),
            teams=_teams(settings),
            token=params.get("token", [""])[0],
            message=params.get("message", [""])[0],
        )
        self._send(200, html)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        params = parse_qs(self.rfile.read(length).decode("utf-8"))
        if not self._authorized(params):
            self._send(403, "Forbidden", "text/plain; charset=utf-8")
            return
        token = params.get("token", [""])[0]
        paths = _paths(self.base)
        settings = self._settings()
        route = urlparse(self.path).path
        if route == "/add-run":
            team_id = int(params["team_id"][0])
            team_name = ""
            for team in _teams(settings):
                if int(team["id"]) == team_id:
                    team_name = team.get("name", "")
                    break
            add_run(
                paths["runs"],
                team_id=team_id,
                team_name=team_name,
                cycles=params["cycles"][0],
                note=params.get("note", [""])[0],
                created_by="web",
            )
            self._redirect(token, _sync_message("Run saved", lambda: _sync(paths, settings)))
        elif route == "/void-run":
            void_run(paths["runs"], int(params["run_id"][0]), "Voided from web UI")
            self._redirect(token, _sync_message("Run voided", lambda: _sync(paths, settings)))
        elif route == "/delete-score":
            delete_score(paths["runs"], int(params["team_id"][0]), "Score deleted from web UI")
            self._redirect(token, _sync_message("Score deleted", lambda: _sync(paths, settings)))
        elif route == "/sync":
            self._redirect(token, _sync_message("Synced", lambda: _sync(paths, settings)))
        else:
            self._send(404, "Not found", "text/plain; charset=utf-8")


def serve(base, host, port):
    handler = type("BoundWatchdogHandler", (WatchdogHandler,), {"base": Path(base)})
    class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
        daemon_threads = True

    server = ThreadingHTTPServer((host, int(port)), handler)
    print("Serving Watchdog KOTH on http://{0}:{1}".format(host, port))
    server.serve_forever()
