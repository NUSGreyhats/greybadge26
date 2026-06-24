from dataclasses import asdict, dataclass, field
import json
from typing import Dict, Optional


@dataclass
class TeamSyncState:
    award_id: Optional[int] = None
    solve_id: Optional[int] = None
    last_score: Optional[int] = None
    last_best_cycles: Optional[int] = None


@dataclass
class SyncState:
    ctfd_url: Optional[str] = None
    challenge_id: Optional[int] = None
    teams: Dict[str, TeamSyncState] = field(default_factory=dict)

    def team(self, team_id):
        key = str(team_id)
        if key not in self.teams:
            self.teams[key] = TeamSyncState()
        return self.teams[key]


def _team_state_from_dict(data):
    return TeamSyncState(
        award_id=data.get("award_id"),
        solve_id=data.get("solve_id"),
        last_score=data.get("last_score"),
        last_best_cycles=data.get("last_best_cycles"),
    )


def load_state(path):
    if not path.exists():
        return SyncState()
    data = json.loads(path.read_text(encoding="utf-8"))
    state = SyncState(
        ctfd_url=data.get("ctfd_url"),
        challenge_id=data.get("challenge_id"),
    )
    state.teams = {
        str(team_id): _team_state_from_dict(team_data)
        for team_id, team_data in data.get("teams", {}).items()
    }
    return state


def save_state(path, state):
    data = asdict(state)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
