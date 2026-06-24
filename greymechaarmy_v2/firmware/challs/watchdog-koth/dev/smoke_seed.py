from CTFd import create_app
from CTFd.models import Awards, Challenges, Configs, Solves, Teams, Users, db

from CTFd.plugins.watchdog_koth.models import (
    WatchdogKothRun,
    WatchdogKothScore,
    get_settings,
)
from CTFd.plugins.watchdog_koth.sync import (
    AWARD_CATEGORY,
    clear_team_score,
    recompute_and_sync,
)


ADMIN_NAME = "watchdog-admin"
ADMIN_PASSWORD = "watchdog-password"
TEAM_ALPHA = "Watchdog Alpha"
TEAM_BETA = "Watchdog Beta"


def ensure_user(name, email, user_type="user", team_id=None):
    user = Users.query.filter_by(name=name).first()
    if user is None:
        user = Users(
            name=name,
            email=email,
            password=ADMIN_PASSWORD,
            type=user_type,
            verified=True,
            hidden=False,
            banned=False,
            team_id=team_id,
        )
        db.session.add(user)
    else:
        user.email = email
        user.password = ADMIN_PASSWORD
        user.type = user_type
        user.verified = True
        user.hidden = False
        user.banned = False
        user.team_id = team_id
    db.session.flush()
    return user


def ensure_team(name, email):
    team = Teams.query.filter_by(name=name).first()
    if team is None:
        team = Teams(
            name=name,
            email=email,
            password=ADMIN_PASSWORD,
            hidden=False,
            banned=False,
        )
        db.session.add(team)
    else:
        team.email = email
        team.password = ADMIN_PASSWORD
        team.hidden = False
        team.banned = False
    db.session.flush()
    user = ensure_user(
        name=name.lower().replace(" ", "-") + "-user",
        email=email,
        user_type="user",
        team_id=team.id,
    )
    team.captain_id = user.id
    db.session.flush()
    return team


def reset_watchdog_data(settings):
    WatchdogKothScore.query.delete()
    WatchdogKothRun.query.delete()
    Awards.query.filter_by(category=AWARD_CATEGORY).delete()
    if settings.challenge_id:
        Solves.query.filter_by(challenge_id=settings.challenge_id).delete()
    db.session.commit()


def set_config(key, value):
    config = Configs.query.filter_by(key=key).first()
    if config is None:
        config = Configs(key=key, value=value)
        db.session.add(config)
    else:
        config.value = value
    db.session.flush()


def main():
    app = create_app()
    with app.app_context():
        set_config("setup", True)
        set_config("ctf_name", "Watchdog KOTH Smoke")
        set_config("user_mode", "teams")
        set_config("challenge_visibility", "public")
        set_config("score_visibility", "public")

        admin = ensure_user(
            ADMIN_NAME,
            "watchdog-admin@example.invalid",
            user_type="admin",
        )
        alpha = ensure_team(TEAM_ALPHA, "watchdog-alpha@example.invalid")
        beta = ensure_team(TEAM_BETA, "watchdog-beta@example.invalid")
        db.session.commit()

        settings = get_settings()
        settings.max_points = 500
        settings.min_points = 1
        settings.challenge_name = "Watchdog KOTH"
        settings.challenge_category = "KOTH"
        settings.award_name = "Watchdog KOTH score"
        db.session.commit()
        reset_watchdog_data(settings)

        db.session.add(
            WatchdogKothRun(
                team_id=alpha.id,
                cycles=100,
                note="smoke alpha",
                created_by_user_id=admin.id,
            )
        )
        db.session.add(
            WatchdogKothRun(
                team_id=beta.id,
                cycles=200,
                note="smoke beta",
                created_by_user_id=admin.id,
            )
        )
        db.session.commit()
        recompute_and_sync()

        settings = get_settings()
        challenge = Challenges.query.get(settings.challenge_id)
        alpha_score = WatchdogKothScore.query.get(alpha.id)
        beta_score = WatchdogKothScore.query.get(beta.id)
        solve_count = Solves.query.filter_by(challenge_id=challenge.id).count()
        award_count = Awards.query.filter_by(category=AWARD_CATEGORY).count()

        assert challenge is not None
        assert challenge.value == 0
        assert alpha_score.score == 500
        assert beta_score.score == 250
        assert solve_count == 2
        assert award_count == 2

        client = app.test_client()
        response = client.get("/api/v1/scoreboard")
        assert response.status_code == 200

        clear_team_score(beta.id, admin.id, "smoke delete score")
        alpha_score = WatchdogKothScore.query.get(alpha.id)
        beta_score = WatchdogKothScore.query.get(beta.id)
        solve_count = Solves.query.filter_by(challenge_id=challenge.id).count()
        award_count = Awards.query.filter_by(category=AWARD_CATEGORY).count()

        assert alpha_score.score == 500
        assert beta_score.score is None
        assert beta_score.solve_id is None
        assert beta_score.award_id is None
        assert solve_count == 1
        assert award_count == 1

        print("admin={0}:{1}".format(ADMIN_NAME, ADMIN_PASSWORD))
        print("challenge_id={0}".format(challenge.id))
        print("alpha_score={0}".format(alpha_score.score))
        print("beta_score_after_delete={0}".format(beta_score.score))
        print("solve_count={0}".format(solve_count))
        print("award_count={0}".format(award_count))
        print("scoreboard_status={0}".format(response.status_code))


if __name__ == "__main__":
    main()
