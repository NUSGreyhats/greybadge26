import argparse
from pathlib import Path

from .config import DEFAULT_RUNS_FILE, DEFAULT_SETTINGS_FILE, DEFAULT_STATE_FILE, load_settings
from .ctfd_client import CtfdClient
from .ledger import add_run, delete_score, import_runs, init_storage, load_runs, void_run
from .scoring import compute_scores
from .state import load_state, save_state
from .sync import sync_scores


def _paths(base):
    base = Path(base)
    return {
        "base": base,
        "settings": base / DEFAULT_SETTINGS_FILE,
        "runs": base / DEFAULT_RUNS_FILE,
        "state": base / DEFAULT_STATE_FILE,
    }


def _client(settings):
    return CtfdClient(settings.ctfd_url, settings.ctfd_token)


def _sync(paths):
    settings = load_settings(paths["settings"])
    state = load_state(paths["state"])
    summary = sync_scores(_client(settings), settings, state, load_runs(paths["runs"]))
    save_state(paths["state"], state)
    return summary


def _maybe_sync(paths, no_sync):
    if no_sync:
        return None
    return _sync(paths)


def _team_name_from_ctfd(settings, team_id):
    try:
        for team in _client(settings).list_teams():
            if int(team["id"]) == int(team_id):
                return team.get("name", "")
    except Exception:
        return ""
    return ""


def cmd_init(args):
    init_storage(Path(args.base))
    print("Initialized Watchdog KOTH API tool storage at {0}".format(Path(args.base)))
    return 0


def cmd_teams(args):
    paths = _paths(args.base)
    settings = load_settings(paths["settings"])
    for team in _client(settings).list_teams():
        print("{id}\t{name}".format(**team))
    return 0


def cmd_add_run(args):
    paths = _paths(args.base)
    settings = load_settings(paths["settings"])
    team_name = args.team_name or _team_name_from_ctfd(settings, args.team_id)
    run = add_run(
        paths["runs"],
        team_id=args.team_id,
        team_name=team_name,
        cycles=args.cycles,
        note=args.note,
        created_by=args.created_by,
    )
    _maybe_sync(paths, args.no_sync)
    print("Added run {0}: team={1} cycles={2}".format(run.run_id, run.team_id, run.cycles))
    return 0


def cmd_void_run(args):
    paths = _paths(args.base)
    run = void_run(paths["runs"], args.run_id, args.reason)
    _maybe_sync(paths, args.no_sync)
    print("Voided run {0}".format(run.run_id))
    return 0


def cmd_delete_score(args):
    paths = _paths(args.base)
    changed = delete_score(paths["runs"], args.team_id, args.reason)
    _maybe_sync(paths, args.no_sync)
    print("Voided {0} active runs for team {1}".format(changed, args.team_id))
    return 0


def cmd_scores(args):
    paths = _paths(args.base)
    settings = load_settings(paths["settings"])
    runs = load_runs(paths["runs"])
    names = {run.team_id: run.team_name for run in runs if run.team_name}
    scores = compute_scores(runs, settings.max_points, settings.min_points)
    print("team_id\tteam_name\tbest_cycles\tscore")
    for team_id in sorted(scores):
        row = scores[team_id]
        print(
            "{0}\t{1}\t{2}\t{3}".format(
                team_id,
                names.get(team_id, ""),
                row["best_cycles"],
                row["score"],
            )
        )
    return 0


def cmd_sync(args):
    paths = _paths(args.base)
    summary = _sync(paths)
    print(
        "Synced challenge={0} scored_teams={1}".format(
            summary["challenge_id"],
            summary["scored_teams"],
        )
    )
    return 0


def cmd_import_csv(args):
    paths = _paths(args.base)
    count = import_runs(paths["runs"], args.path)
    _maybe_sync(paths, args.no_sync)
    print("Imported {0} runs".format(count))
    return 0


def cmd_serve(args):
    from .web import serve

    paths = _paths(args.base)
    settings = load_settings(paths["settings"])
    serve(paths["base"], settings.web_host, settings.web_port)
    return 0


def build_parser():
    parser = argparse.ArgumentParser(description="Watchdog KOTH no-plugin CTFd API tool")
    parser.add_argument("--base", default=".", help="directory with settings/runs/state files")
    sub = parser.add_subparsers(dest="command")

    init = sub.add_parser("init")
    init.set_defaults(func=cmd_init)

    teams = sub.add_parser("teams")
    teams.set_defaults(func=cmd_teams)

    add = sub.add_parser("add-run")
    add.add_argument("--team-id", required=True, type=int)
    add.add_argument("--team-name", default="")
    add.add_argument("--cycles", required=True)
    add.add_argument("--note", default="")
    add.add_argument("--created-by", default="")
    add.add_argument("--no-sync", action="store_true")
    add.set_defaults(func=cmd_add_run)

    void = sub.add_parser("void-run")
    void.add_argument("--run-id", required=True, type=int)
    void.add_argument("--reason", default="Voided by operator")
    void.add_argument("--no-sync", action="store_true")
    void.set_defaults(func=cmd_void_run)

    delete = sub.add_parser("delete-score")
    delete.add_argument("--team-id", required=True, type=int)
    delete.add_argument("--reason", default="Score deleted by operator")
    delete.add_argument("--no-sync", action="store_true")
    delete.set_defaults(func=cmd_delete_score)

    scores = sub.add_parser("scores")
    scores.set_defaults(func=cmd_scores)

    sync = sub.add_parser("sync")
    sync.set_defaults(func=cmd_sync)

    import_csv = sub.add_parser("import-csv")
    import_csv.add_argument("path")
    import_csv.add_argument("--no-sync", action="store_true")
    import_csv.set_defaults(func=cmd_import_csv)

    serve = sub.add_parser("serve")
    serve.set_defaults(func=cmd_serve)
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 2
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
