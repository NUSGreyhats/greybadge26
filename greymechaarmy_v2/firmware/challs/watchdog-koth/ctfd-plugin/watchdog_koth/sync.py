from datetime import datetime

from CTFd.cache import cache
from CTFd.models import Awards, Challenges, Solves, Teams, Users, db

from .models import WatchdogKothRun, WatchdogKothScore, get_settings
from .scoring import compute_scores


AWARD_CATEGORY = "watchdog-koth"


def _set_if_present(obj, name, value):
    if hasattr(obj, name):
        setattr(obj, name, value)


def _challenge_kwargs(settings):
    return {
        "name": settings.challenge_name,
        "category": settings.challenge_category,
        "description": settings.challenge_description,
        "value": 0,
        "type": "standard",
        "state": "visible",
    }


def ensure_challenge(settings=None):
    settings = settings or get_settings()
    challenge = None
    if settings.challenge_id:
        challenge = Challenges.query.get(settings.challenge_id)

    if challenge is None:
        challenge = Challenges(**_challenge_kwargs(settings))
        db.session.add(challenge)
        db.session.flush()
        settings.challenge_id = challenge.id
    else:
        for key, value in _challenge_kwargs(settings).items():
            if hasattr(challenge, key):
                setattr(challenge, key, value)
    return challenge


def get_team_carrier_user(team):
    captain_id = getattr(team, "captain_id", None)
    if captain_id:
        captain = Users.query.get(captain_id)
        if captain is not None:
            return captain
    return Users.query.filter_by(team_id=team.id).order_by(Users.id.asc()).first()


def _all_runs():
    return WatchdogKothRun.query.order_by(WatchdogKothRun.created_at.asc()).all()


def _upsert_solve(score_row, team, user, challenge):
    solve = Solves.query.get(score_row.solve_id) if score_row.solve_id else None
    if solve is None:
        solve = (
            Solves.query.filter_by(team_id=team.id, challenge_id=challenge.id)
            .order_by(Solves.id.asc())
            .first()
        )
    if solve is None:
        solve = Solves(
            challenge_id=challenge.id,
            user_id=user.id,
            team_id=team.id,
            ip="127.0.0.1",
            provided="watchdog-koth",
        )
        db.session.add(solve)
        db.session.flush()
    else:
        solve.challenge_id = challenge.id
        solve.user_id = user.id
        solve.team_id = team.id
        _set_if_present(solve, "provided", "watchdog-koth")
    score_row.solve_id = solve.id
    return solve


def _upsert_award(score_row, team, user, settings, current_score):
    award = Awards.query.get(score_row.award_id) if score_row.award_id else None
    if award is None:
        award = (
            Awards.query.filter_by(
                team_id=team.id,
                category=AWARD_CATEGORY,
                name=settings.award_name,
            )
            .order_by(Awards.id.asc())
            .first()
        )
    description = "Best watchdog run: {0} cycles".format(current_score["best_cycles"])
    if award is None:
        award = Awards(
            name=settings.award_name,
            value=current_score["score"],
            category=AWARD_CATEGORY,
            description=description,
            user_id=user.id,
            team_id=team.id,
        )
        db.session.add(award)
        db.session.flush()
    else:
        award.name = settings.award_name
        award.value = current_score["score"]
        award.category = AWARD_CATEGORY
        award.description = description
        award.user_id = user.id
        _set_if_present(award, "team_id", team.id)
    score_row.award_id = award.id
    return award


def _delete_artifacts(score_row):
    solve_id = score_row.solve_id
    award_id = score_row.award_id
    score_row.solve_id = None
    score_row.award_id = None
    db.session.flush()

    if solve_id:
        solve = Solves.query.get(solve_id)
        if solve is not None:
            db.session.delete(solve)
    if award_id:
        award = Awards.query.get(award_id)
        if award is not None:
            db.session.delete(award)


def _cache_clear():
    try:
        cache.clear()
    except Exception:
        pass


def clear_team_score(team_id, admin_user_id=None, reason=None):
    now = datetime.utcnow()
    reason = reason or "Score deleted by admin"
    active_runs = WatchdogKothRun.query.filter_by(
        team_id=team_id,
        voided_at=None,
    ).all()
    for run in active_runs:
        run.voided_at = now
        run.voided_by_user_id = admin_user_id
        run.void_reason = reason
    db.session.commit()
    return recompute_and_sync()


def recompute_and_sync():
    settings = get_settings()
    challenge = ensure_challenge(settings)
    runs = _all_runs()
    computed = compute_scores(
        runs,
        max_points=settings.max_points,
        min_points=settings.min_points,
    )
    for team in Teams.query.order_by(Teams.id.asc()).all():
        score_row = WatchdogKothScore.query.get(team.id)
        if score_row is None:
            score_row = WatchdogKothScore(team_id=team.id)
            db.session.add(score_row)

        current_score = computed.get(team.id)
        if current_score is None:
            _delete_artifacts(score_row)
            score_row.best_run_id = None
            score_row.best_cycles = None
            score_row.score = None
            score_row.synced_at = datetime.utcnow()
            score_row.sync_error = None
            continue

        score_row.best_run_id = current_score["best_run_id"]
        score_row.best_cycles = current_score["best_cycles"]
        score_row.score = current_score["score"]
        user = get_team_carrier_user(team)
        if user is None:
            score_row.sync_error = "Team has no users to carry CTFd solve/award"
            _delete_artifacts(score_row)
            score_row.synced_at = datetime.utcnow()
            continue

        _upsert_solve(score_row, team, user, challenge)
        _upsert_award(score_row, team, user, settings, current_score)
        score_row.sync_error = None
        score_row.synced_at = datetime.utcnow()

    db.session.commit()
    _cache_clear()
    return computed
