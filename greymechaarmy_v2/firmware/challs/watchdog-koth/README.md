# Watchdog KOTH CTFd Plugin

This folder contains the GreyMecha watchdog KOTH CTFd plugin and its local
development harness. The plugin is intentionally manual-entry first: admins
enter measured clock-cycle counts per team, and the plugin computes CTFd scores.

## Layout

- `ctfd-plugin/watchdog_koth/` - CTFd plugin package.
- `api-tool/watchdog_koth_api/` - standalone no-plugin CTFd API tool.
- `tests/` - local unit tests for scoring behavior.
- `dev/docker-compose.yml` - local CTFd instance with the plugin mounted.
- `dev/docker-compose.api.yml` - local CTFd instance with only the API tool
  mounted, not the plugin.

## Scoring

Scores are calculated from each team's best non-voided cycle count:

```text
score = clamp(round(max_points * fastest_cycles / team_best_cycles), min_points, max_points)
```

Lower cycle counts are better. Ties share the same score.

The plugin creates or updates:

- one 0-point CTFd Standard challenge for solve visibility,
- one CTFd Solve per scored team,
- one CTFd Award per scored team for the calculated KOTH points.

## Local Unit Tests

From the repository root:

```powershell
python -m unittest greymechaarmy_v2/firmware/challs/watchdog-koth/tests/test_scoring.py
```

## Setting Up A New CTFd

The preferred setup is now the no-plugin API tool. It stores KOTH runs locally
in CSV and syncs CTFd through an admin access token.

Create an admin access token in CTFd, then run from this folder or pass
`--base` to choose a storage directory:

```powershell
$env:CTFD_TOKEN = "<admin access token>"
$env:PYTHONPATH = "api-tool"
python -m watchdog_koth_api --base api-state init
```

Edit `api-state/settings.json` if your CTFd URL is not `http://localhost:8000`.
Then add runs and sync scores:

```powershell
python -m watchdog_koth_api --base api-state teams
python -m watchdog_koth_api --base api-state add-run --team-id 1 --team-name "Team One" --cycles 150
python -m watchdog_koth_api --base api-state add-run --team-id 2 --team-name "Team Two" --cycles 0x96
python -m watchdog_koth_api --base api-state scores
python -m watchdog_koth_api --base api-state sync
```

The API tool creates and keeps synced:

- a 0-point `Watchdog KOTH` Standard challenge for solve visibility,
- one native CTFd Solve per scored team,
- one CTFd Award per scored team for the calculated KOTH points.

To clear a team's score without deleting history:

```powershell
python -m watchdog_koth_api --base api-state delete-score --team-id 2 --reason "bad measurement"
```

To run the local web UI:

```powershell
$env:WATCHDOG_KOTH_WEB_TOKEN = "change-me"
python -m watchdog_koth_api --base api-state serve
```

Open `http://127.0.0.1:8765/?token=change-me`. The web UI is intended for
local/internal operation only.

## Legacy CTFd Plugin Setup

Install the plugin by making this package:

```text
greymechaarmy_v2/firmware/challs/watchdog-koth/ctfd-plugin/watchdog_koth
```

available inside the CTFd container or host at:

```text
/opt/CTFd/CTFd/plugins/watchdog_koth
```

For a Docker Compose CTFd service, add a read-only bind mount like this:

```yaml
volumes:
  - ./greymechaarmy_v2/firmware/challs/watchdog-koth/ctfd-plugin/watchdog_koth:/opt/CTFd/CTFd/plugins/watchdog_koth:ro
```

Then restart CTFd:

```powershell
docker compose down
docker compose up -d
```

After CTFd starts:

1. Complete the normal CTFd setup wizard.
2. Enable team mode.
3. Create teams and make sure each scored team has at least one member.
4. Visit `/admin/watchdog-koth`.
5. Enter cycle counts for each team. Decimal values such as `150` and prefixed
   hexadecimal values such as `0x96` are both accepted.

The plugin creates and keeps synced:

- a 0-point `Watchdog KOTH` Standard challenge for solve visibility,
- one CTFd Solve per scored team,
- one CTFd Award per scored team for the calculated KOTH points.

Use **Resync all** from `/admin/watchdog-koth` if CTFd solves or awards are
edited outside the plugin. Use **Delete score** to clear a team's active KOTH
score; this voids that team's active runs and removes the synced solve and
award.

## Local CTFd Smoke Test

From `greymechaarmy_v2/firmware/challs/watchdog-koth/dev`:

```powershell
docker compose up -d
```

Then open `http://localhost:8000`, complete the normal CTFd setup, enable team
mode, create at least two teams with one member each, and visit:

```text
/admin/watchdog-koth
```

Enter cycle counts for the teams. Cycle counts may be decimal, such as `150`,
or prefixed hexadecimal, such as `0x96`.

Verify:

- the team table shows best cycles and scores,
- CTFd shows the plugin-managed `Watchdog KOTH` challenge,
- teams with cycle entries have a solve for that challenge,
- the native CTFd scoreboard includes the KOTH Award points.
- **Delete score** clears a team's active KOTH score by voiding that team's
  active runs and removing its synced CTFd solve and award.

Use **Resync all** if CTFd awards or solves are edited outside the plugin.

You can seed a disposable local smoke dataset from the repository root:

```powershell
docker compose -f greymechaarmy_v2/firmware/challs/watchdog-koth/dev/docker-compose.yml cp greymechaarmy_v2/firmware/challs/watchdog-koth/dev/smoke_seed.py ctfd:/tmp/watchdog_smoke_seed.py
docker compose -f greymechaarmy_v2/firmware/challs/watchdog-koth/dev/docker-compose.yml exec -T ctfd sh -lc "PYTHONPATH=/opt/CTFd /opt/venv/bin/python /tmp/watchdog_smoke_seed.py"
```

The seeded admin login is `watchdog-admin` / `watchdog-password`. The smoke
script resets Watchdog KOTH plugin rows in the local CTFd database, creates two
teams, inserts cycle runs, syncs CTFd solves and awards, checks score deletion,
checks decimal and hexadecimal cycle input, and checks that the scoreboard API
returns HTTP 200.

## Local No-Plugin API Smoke Test

From the repository root, copy the smoke script into the no-plugin container
and run it:

```powershell
docker compose -p watchdog_api -f greymechaarmy_v2/firmware/challs/watchdog-koth/dev/docker-compose.api.yml up -d
docker compose -p watchdog_api -f greymechaarmy_v2/firmware/challs/watchdog-koth/dev/docker-compose.api.yml cp greymechaarmy_v2/firmware/challs/watchdog-koth/dev/api_smoke.py ctfd:/tmp/watchdog_api_smoke.py
docker compose -p watchdog_api -f greymechaarmy_v2/firmware/challs/watchdog-koth/dev/docker-compose.api.yml exec -T ctfd sh -lc "PYTHONPATH=/opt/CTFd /opt/venv/bin/python /tmp/watchdog_api_smoke.py"
```

The API smoke verifies that CTFd runs without the `watchdog_koth` plugin
mounted, then uses the standalone API tool to initialize storage, add decimal
and hexadecimal runs, sync challenge solves and awards, delete one team's score,
and check the scoreboard API.
