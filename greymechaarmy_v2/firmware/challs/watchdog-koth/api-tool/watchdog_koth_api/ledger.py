from dataclasses import dataclass
import csv
from datetime import datetime, timezone
from pathlib import Path

from .config import (
    DEFAULT_RUNS_FILE,
    DEFAULT_SETTINGS_FILE,
    DEFAULT_STATE_FILE,
    Settings,
    save_settings,
)
from .scoring import validate_cycles
from .state import SyncState, save_state


RUN_FIELDS = [
    "run_id",
    "team_id",
    "team_name",
    "cycles",
    "note",
    "created_at",
    "created_by",
    "voided_at",
    "void_reason",
]


@dataclass
class Run:
    run_id: int
    team_id: int
    team_name: str
    cycles: int
    note: str = ""
    created_at: str = ""
    created_by: str = ""
    voided_at: str = ""
    void_reason: str = ""


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def init_storage(base):
    base = Path(base)
    base.mkdir(parents=True, exist_ok=True)
    settings_path = base / DEFAULT_SETTINGS_FILE
    runs_path = base / DEFAULT_RUNS_FILE
    state_path = base / DEFAULT_STATE_FILE
    if not settings_path.exists():
        save_settings(settings_path, Settings())
    if not runs_path.exists():
        _write_runs(runs_path, [])
    if not state_path.exists():
        save_state(state_path, SyncState())


def _run_from_row(row):
    return Run(
        run_id=int(row["run_id"]),
        team_id=int(row["team_id"]),
        team_name=row.get("team_name", ""),
        cycles=validate_cycles(row["cycles"]),
        note=row.get("note", ""),
        created_at=row.get("created_at", ""),
        created_by=row.get("created_by", ""),
        voided_at=row.get("voided_at", ""),
        void_reason=row.get("void_reason", ""),
    )


def _row_from_run(run):
    return {
        "run_id": run.run_id,
        "team_id": run.team_id,
        "team_name": run.team_name,
        "cycles": run.cycles,
        "note": run.note,
        "created_at": run.created_at,
        "created_by": run.created_by,
        "voided_at": run.voided_at,
        "void_reason": run.void_reason,
    }


def load_runs(path):
    path = Path(path)
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return [_run_from_row(row) for row in reader]


def _write_runs(path, runs):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=RUN_FIELDS)
        writer.writeheader()
        for run in runs:
            writer.writerow(_row_from_run(run))


def _next_run_id(runs):
    if not runs:
        return 1
    return max(run.run_id for run in runs) + 1


def add_run(path, team_id, team_name, cycles, note="", created_by="", now=None):
    runs = load_runs(path)
    run = Run(
        run_id=_next_run_id(runs),
        team_id=int(team_id),
        team_name=str(team_name),
        cycles=validate_cycles(cycles),
        note=note or "",
        created_at=now or utc_now(),
        created_by=created_by or "",
    )
    runs.append(run)
    _write_runs(path, runs)
    return run


def void_run(path, run_id, reason, now=None):
    runs = load_runs(path)
    target = None
    for run in runs:
        if run.run_id == int(run_id):
            target = run
            break
    if target is None:
        raise ValueError("run_id does not exist")
    if not target.voided_at:
        target.voided_at = now or utc_now()
        target.void_reason = reason or "Voided by operator"
    _write_runs(path, runs)
    return target


def delete_score(path, team_id, reason, now=None):
    runs = load_runs(path)
    timestamp = now or utc_now()
    changed = 0
    for run in runs:
        if run.team_id == int(team_id) and not run.voided_at:
            run.voided_at = timestamp
            run.void_reason = reason or "Score deleted by operator"
            changed += 1
    _write_runs(path, runs)
    return changed


def import_runs(path, incoming_path, now=None):
    count = 0
    with Path(incoming_path).open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            add_run(
                path,
                team_id=row["team_id"],
                team_name=row.get("team_name", ""),
                cycles=row["cycles"],
                note=row.get("note", ""),
                created_by=row.get("created_by", ""),
                now=row.get("created_at") or now,
            )
            count += 1
    return count
