from datetime import datetime
import os

from flask import flash, redirect, render_template, request, url_for
from jinja2 import ChoiceLoader, FileSystemLoader

from CTFd.models import Teams, db
from CTFd.utils.decorators import admins_only
from CTFd.utils.user import get_current_user

from .models import (
    DEFAULT_CHALLENGE_CATEGORY,
    DEFAULT_CHALLENGE_DESCRIPTION,
    DEFAULT_CHALLENGE_NAME,
    DEFAULT_MAX_POINTS,
    DEFAULT_MIN_POINTS,
    WatchdogKothRun,
    WatchdogKothScore,
    get_settings,
)
from .scoring import validate_cycles
from .sync import recompute_and_sync


def _current_user_id():
    user = get_current_user()
    return user.id if user is not None else None


def _teams_with_scores():
    scores = {
        score.team_id: score for score in WatchdogKothScore.query.order_by(
            WatchdogKothScore.team_id.asc()
        ).all()
    }
    teams = Teams.query.order_by(Teams.name.asc()).all()
    return [(team, scores.get(team.id)) for team in teams]


def _recent_runs(limit=25):
    return (
        WatchdogKothRun.query.order_by(WatchdogKothRun.created_at.desc())
        .limit(limit)
        .all()
    )


def _install_template_loader(app):
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    loader = FileSystemLoader(template_dir)
    if isinstance(app.jinja_loader, ChoiceLoader):
        app.jinja_loader.loaders.insert(0, loader)
    else:
        app.jinja_loader = ChoiceLoader([loader, app.jinja_loader])


def register_routes(app):
    _install_template_loader(app)

    @app.route("/admin/watchdog-koth", methods=["GET"])
    @admins_only
    def watchdog_koth_admin():
        settings = get_settings()
        return render_template(
            "watchdog_koth/admin.html",
            settings=settings,
            teams_with_scores=_teams_with_scores(),
            teams_by_id={team.id: team for team in Teams.query.all()},
            recent_runs=_recent_runs(),
            defaults={
                "challenge_name": DEFAULT_CHALLENGE_NAME,
                "challenge_category": DEFAULT_CHALLENGE_CATEGORY,
                "challenge_description": DEFAULT_CHALLENGE_DESCRIPTION,
                "max_points": DEFAULT_MAX_POINTS,
                "min_points": DEFAULT_MIN_POINTS,
            },
        )

    @app.route("/admin/watchdog-koth/settings", methods=["POST"])
    @admins_only
    def watchdog_koth_settings():
        settings = get_settings()
        try:
            max_points = int(request.form.get("max_points", DEFAULT_MAX_POINTS))
            min_points = int(request.form.get("min_points", DEFAULT_MIN_POINTS))
            if min_points < 0 or max_points < min_points:
                raise ValueError
        except ValueError:
            flash("Point bounds must be integers with max >= min >= 0.", "danger")
            return redirect(url_for("watchdog_koth_admin"))

        settings.challenge_name = request.form.get("challenge_name") or DEFAULT_CHALLENGE_NAME
        settings.challenge_category = (
            request.form.get("challenge_category") or DEFAULT_CHALLENGE_CATEGORY
        )
        settings.challenge_description = (
            request.form.get("challenge_description") or DEFAULT_CHALLENGE_DESCRIPTION
        )
        settings.award_name = request.form.get("award_name") or "Watchdog KOTH score"
        settings.max_points = max_points
        settings.min_points = min_points
        settings.updated_at = datetime.utcnow()
        db.session.commit()
        recompute_and_sync()
        flash("Watchdog KOTH settings saved and scores resynced.", "success")
        return redirect(url_for("watchdog_koth_admin"))

    @app.route("/admin/watchdog-koth/runs", methods=["POST"])
    @admins_only
    def watchdog_koth_add_run():
        try:
            team_id = int(request.form.get("team_id", ""))
            cycles = validate_cycles(request.form.get("cycles"))
        except ValueError:
            flash("Team and cycles are required; cycles must be positive.", "danger")
            return redirect(url_for("watchdog_koth_admin"))

        if Teams.query.get(team_id) is None:
            flash("Selected team does not exist.", "danger")
            return redirect(url_for("watchdog_koth_admin"))

        run = WatchdogKothRun(
            team_id=team_id,
            cycles=cycles,
            note=request.form.get("note") or None,
            created_by_user_id=_current_user_id(),
        )
        db.session.add(run)
        db.session.commit()
        recompute_and_sync()
        flash("Watchdog KOTH run saved and scores resynced.", "success")
        return redirect(url_for("watchdog_koth_admin"))

    @app.route("/admin/watchdog-koth/runs/<int:run_id>/void", methods=["POST"])
    @admins_only
    def watchdog_koth_void_run(run_id):
        run = WatchdogKothRun.query.get_or_404(run_id)
        if run.voided_at is None:
            run.voided_at = datetime.utcnow()
            run.voided_by_user_id = _current_user_id()
            run.void_reason = request.form.get("void_reason") or "Voided by admin"
            db.session.commit()
            recompute_and_sync()
            flash("Run voided and scores resynced.", "success")
        else:
            flash("Run was already voided.", "warning")
        return redirect(url_for("watchdog_koth_admin"))

    @app.route("/admin/watchdog-koth/resync", methods=["POST"])
    @admins_only
    def watchdog_koth_resync():
        recompute_and_sync()
        flash("Watchdog KOTH scores resynced.", "success")
        return redirect(url_for("watchdog_koth_admin"))
