from datetime import datetime

from CTFd.models import db


DEFAULT_CHALLENGE_NAME = "Watchdog KOTH"
DEFAULT_CHALLENGE_CATEGORY = "KOTH"
DEFAULT_CHALLENGE_DESCRIPTION = (
    "GreyMecha watchdog king-of-the-hill challenge. Scores are based on "
    "manually entered clock-cycle measurements."
)
DEFAULT_AWARD_NAME = "Watchdog KOTH score"
DEFAULT_MAX_POINTS = 500
DEFAULT_MIN_POINTS = 1


class WatchdogKothSettings(db.Model):
    __tablename__ = "watchdog_koth_settings"

    id = db.Column(db.Integer, primary_key=True)
    challenge_id = db.Column(db.Integer, db.ForeignKey("challenges.id"), nullable=True)
    challenge_name = db.Column(db.String(128), nullable=False, default=DEFAULT_CHALLENGE_NAME)
    challenge_category = db.Column(
        db.String(80), nullable=False, default=DEFAULT_CHALLENGE_CATEGORY
    )
    challenge_description = db.Column(
        db.Text, nullable=False, default=DEFAULT_CHALLENGE_DESCRIPTION
    )
    award_name = db.Column(db.String(128), nullable=False, default=DEFAULT_AWARD_NAME)
    max_points = db.Column(db.Integer, nullable=False, default=DEFAULT_MAX_POINTS)
    min_points = db.Column(db.Integer, nullable=False, default=DEFAULT_MIN_POINTS)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class WatchdogKothRun(db.Model):
    __tablename__ = "watchdog_koth_runs"

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=False, index=True)
    cycles = db.Column(db.Integer, nullable=False)
    note = db.Column(db.Text, nullable=True)
    created_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    voided_at = db.Column(db.DateTime, nullable=True)
    voided_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    void_reason = db.Column(db.Text, nullable=True)


class WatchdogKothScore(db.Model):
    __tablename__ = "watchdog_koth_scores"

    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"), primary_key=True)
    best_run_id = db.Column(
        db.Integer, db.ForeignKey("watchdog_koth_runs.id"), nullable=True
    )
    best_cycles = db.Column(db.Integer, nullable=True)
    score = db.Column(db.Integer, nullable=True)
    solve_id = db.Column(db.Integer, db.ForeignKey("submissions.id"), nullable=True)
    award_id = db.Column(db.Integer, db.ForeignKey("awards.id"), nullable=True)
    synced_at = db.Column(db.DateTime, nullable=True)
    sync_error = db.Column(db.Text, nullable=True)


def get_settings():
    settings = WatchdogKothSettings.query.get(1)
    if settings is None:
        settings = WatchdogKothSettings(id=1)
        db.session.add(settings)
        db.session.commit()
    return settings


def create_tables():
    db.create_all()
    get_settings()
