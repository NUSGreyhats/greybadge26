from dataclasses import asdict, dataclass
import json
import os


DEFAULT_SETTINGS_FILE = "settings.json"
DEFAULT_RUNS_FILE = "runs.csv"
DEFAULT_STATE_FILE = "sync_state.json"


@dataclass
class Settings:
    ctfd_url: str = "http://localhost:8000"
    token_env: str = "CTFD_TOKEN"
    challenge_name: str = "Watchdog KOTH"
    challenge_category: str = "KOTH"
    challenge_description: str = (
        "GreyMecha watchdog king-of-the-hill challenge. Scores are based on "
        "manually entered clock-cycle measurements."
    )
    award_name: str = "Watchdog KOTH score"
    max_points: int = 500
    min_points: int = 1
    solve_sync: bool = True
    web_host: str = "127.0.0.1"
    web_port: int = 8765
    web_token_env: str = "WATCHDOG_KOTH_WEB_TOKEN"

    @property
    def ctfd_token(self):
        return os.environ.get(self.token_env)

    @property
    def web_token(self):
        return os.environ.get(self.web_token_env, "watchdog-koth-local")


def load_settings(path):
    if not path.exists():
        return Settings()
    data = json.loads(path.read_text(encoding="utf-8"))
    return Settings(**{**asdict(Settings()), **data})


def save_settings(path, settings):
    path.write_text(
        json.dumps(asdict(settings), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
