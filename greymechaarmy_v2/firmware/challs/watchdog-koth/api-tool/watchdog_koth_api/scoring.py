def validate_cycles(value):
    text = str(value).strip()
    base = 16 if text.lower().startswith("0x") else 10
    try:
        cycles = int(text, base)
    except (TypeError, ValueError):
        raise ValueError("cycles must be a positive integer")
    if cycles <= 0:
        raise ValueError("cycles must be a positive integer")
    return cycles


def _is_voided(run):
    if hasattr(run, "voided_at"):
        return bool(getattr(run, "voided_at"))
    return bool(run.get("voided_at") or run.get("voided"))


def _field(run, name):
    if isinstance(run, dict):
        return run.get(name)
    return getattr(run, name, None)


def _clamp(value, min_points, max_points):
    return max(min_points, min(max_points, value))


def compute_scores(runs, max_points, min_points):
    max_points = int(max_points)
    min_points = int(min_points)
    if min_points < 0:
        raise ValueError("min_points must be non-negative")
    if max_points < min_points:
        raise ValueError("max_points must be greater than or equal to min_points")

    best_by_team = {}
    for run in runs:
        if _is_voided(run):
            continue
        team_id = int(_field(run, "team_id"))
        run_id = _field(run, "run_id") or _field(run, "id")
        cycles = validate_cycles(_field(run, "cycles"))
        current = best_by_team.get(team_id)
        if current is None or cycles < current["best_cycles"]:
            best_by_team[team_id] = {
                "team_id": team_id,
                "best_run_id": int(run_id),
                "best_cycles": cycles,
            }

    if not best_by_team:
        return {}

    fastest_cycles = min(row["best_cycles"] for row in best_by_team.values())
    scores = {}
    for team_id, row in best_by_team.items():
        raw_score = int(round(float(max_points) * fastest_cycles / row["best_cycles"]))
        row = dict(row)
        row["score"] = _clamp(raw_score, min_points, max_points)
        scores[team_id] = row
    return scores
