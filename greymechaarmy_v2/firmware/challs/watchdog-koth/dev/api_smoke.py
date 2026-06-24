import json
import os
import shutil
import sys
import threading
import time
from pathlib import Path
from urllib import request

from CTFd import create_app
from CTFd.models import Awards, Challenges, Configs, Solves, Teams, Tokens, Users, db
from werkzeug.serving import make_server


API_TOOL_ROOT = Path("/opt/watchdog-koth-api-tool")
WORKDIR = Path("/tmp/watchdog-koth-api-smoke")
TOKEN_VALUE = "watchdog-koth-api-smoke-token"
ADMIN_PASSWORD = "watchdog-password"
AWARD_CATEGORY = "watchdog-koth"
CHALLENGE_NAME = "Watchdog KOTH"
API_BASE_URL = "http://127.0.0.1:9000"


sys.path.insert(0, str(API_TOOL_ROOT))


def set_config(key, value):
    config = Configs.query.filter_by(key=key).first()
    if config is None:
        config = Configs(key=key, value=value)
        db.session.add(config)
    else:
        config.value = value
    db.session.flush()


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
        team = Teams(name=name, email=email, password=ADMIN_PASSWORD, hidden=False, banned=False)
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


def ensure_token(admin):
    token = Tokens.query.filter_by(value=TOKEN_VALUE).first()
    if token is None:
        token = Tokens(
            type="user",
            user_id=admin.id,
            description="Watchdog KOTH API smoke",
            value=TOKEN_VALUE,
        )
        db.session.add(token)
    else:
        token.user_id = admin.id
        token.type = "user"
        token.description = "Watchdog KOTH API smoke"
    db.session.flush()
    return token


def reset_koth_data():
    challenge = Challenges.query.filter_by(name=CHALLENGE_NAME).first()
    if challenge is not None:
        Solves.query.filter_by(challenge_id=challenge.id).delete()
        db.session.delete(challenge)
    Awards.query.filter_by(category=AWARD_CATEGORY).delete()
    db.session.commit()


def api_get(path):
    req = request.Request(
        "{0}{1}".format(API_BASE_URL, path),
        headers={
            "Authorization": "Token {0}".format(TOKEN_VALUE),
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    with request.urlopen(req, timeout=15) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def main():
    if (Path("/opt/CTFd/CTFd/plugins") / "watchdog_koth").exists():
        raise AssertionError("watchdog_koth plugin directory is mounted")

    app = create_app()
    with app.app_context():
        set_config("setup", True)
        set_config("ctf_name", "Watchdog KOTH API Smoke")
        set_config("user_mode", "teams")
        set_config("challenge_visibility", "public")
        set_config("score_visibility", "public")

        admin = ensure_user("watchdog-admin", "watchdog-admin@example.invalid", "admin")
        alpha = ensure_team("Watchdog Alpha", "watchdog-alpha@example.invalid")
        beta = ensure_team("Watchdog Beta", "watchdog-beta@example.invalid")
        ensure_token(admin)
        reset_koth_data()
        db.session.commit()
        alpha_id = alpha.id
        alpha_name = alpha.name
        beta_id = beta.id
        beta_name = beta.name

    server = make_server("127.0.0.1", 9000, app)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    time.sleep(0.5)

    if WORKDIR.exists():
        shutil.rmtree(str(WORKDIR))
    WORKDIR.mkdir(parents=True)
    os.environ["CTFD_TOKEN"] = TOKEN_VALUE

    from watchdog_koth_api.cli import main as cli_main
    from watchdog_koth_api.config import load_settings, save_settings

    assert cli_main(["--base", str(WORKDIR), "init"]) == 0
    settings_path = WORKDIR / "settings.json"
    settings = load_settings(settings_path)
    settings.ctfd_url = API_BASE_URL
    save_settings(settings_path, settings)
    assert cli_main(
        [
            "--base",
            str(WORKDIR),
            "add-run",
            "--team-id",
            str(alpha_id),
            "--team-name",
            alpha_name,
            "--cycles",
            "100",
        ]
    ) == 0
    assert cli_main(
        [
            "--base",
            str(WORKDIR),
            "add-run",
            "--team-id",
            str(beta_id),
            "--team-name",
            beta_name,
            "--cycles",
            "0xc8",
        ]
    ) == 0

    with app.app_context():
        challenge = Challenges.query.filter_by(name=CHALLENGE_NAME).first()
        assert challenge is not None
        assert challenge.value == 0
        solve_count = Solves.query.filter_by(challenge_id=challenge.id).count()
        award_count = Awards.query.filter_by(category=AWARD_CATEGORY).count()
        assert solve_count == 2
        assert award_count == 2

    status, scoreboard = api_get("/api/v1/scoreboard")
    assert status == 200
    assert scoreboard["success"] is True

    status, beta_solves = api_get("/api/v1/teams/{0}/solves".format(beta_id))
    assert status == 200
    assert any(row["challenge"]["name"] == CHALLENGE_NAME for row in beta_solves["data"])

    assert cli_main(
        [
            "--base",
            str(WORKDIR),
            "delete-score",
            "--team-id",
            str(beta_id),
            "--reason",
            "smoke delete",
        ]
    ) == 0

    with app.app_context():
        challenge = Challenges.query.filter_by(name=CHALLENGE_NAME).first()
        solve_count = Solves.query.filter_by(challenge_id=challenge.id).count()
        award_count = Awards.query.filter_by(category=AWARD_CATEGORY).count()
        assert solve_count == 1
        assert award_count == 1

    print("api_tool_base={0}".format(WORKDIR))
    print("challenge_id={0}".format(challenge.id))
    print("solve_count={0}".format(solve_count))
    print("award_count={0}".format(award_count))
    print("scoreboard_status={0}".format(status))
    print("plugin_mounted=false")
    server.shutdown()


if __name__ == "__main__":
    main()
