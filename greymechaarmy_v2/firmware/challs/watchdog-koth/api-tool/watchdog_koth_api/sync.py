from .scoring import compute_scores


def _challenge_payload(settings):
    return {
        "name": settings.challenge_name,
        "category": settings.challenge_category,
        "description": settings.challenge_description,
        "value": 0,
        "type": "standard",
        "state": "visible",
    }


def ensure_challenge(client, settings, state):
    payload = _challenge_payload(settings)
    challenge = None
    if state.challenge_id:
        for existing in client.list_challenges():
            if existing.get("id") == state.challenge_id:
                challenge = existing
                break
    if challenge is None:
        for existing in client.list_challenges():
            if existing.get("name") == settings.challenge_name:
                challenge = existing
                state.challenge_id = existing.get("id")
                break
    if challenge is None:
        challenge = client.create_challenge(payload)
        state.challenge_id = challenge["id"]
        return challenge
    client.update_challenge(state.challenge_id, payload)
    return {**challenge, **payload, "id": state.challenge_id}


def _teams_by_id(client):
    return {int(team["id"]): team for team in client.list_teams()}


def _carrier_user_id(client, team_id):
    members = client.list_team_members(team_id)
    if not members:
        return None
    first = members[0]
    if isinstance(first, dict):
        return int(first["id"])
    return int(first)


def _delete_team_artifacts(client, team_state):
    if team_state.award_id:
        if client.get_award(team_state.award_id) is not None:
            client.delete_award(team_state.award_id)
        team_state.award_id = None
    if team_state.solve_id:
        if client.get_submission(team_state.solve_id) is not None:
            client.delete_submission(team_state.solve_id)
        team_state.solve_id = None
    team_state.last_score = None
    team_state.last_best_cycles = None


def _matching_awards(client, settings, team_id):
    return [
        award
        for award in client.list_team_awards(team_id)
        if award.get("category") == "watchdog-koth"
        and award.get("name") == settings.award_name
    ]


def _award_matches(award, current_score):
    description = "Best watchdog run: {0} cycles".format(current_score["best_cycles"])
    return (
        int(award.get("value", -1)) == int(current_score["score"])
        and award.get("description") == description
    )


def _sync_award(client, settings, team_id, user_id, team_state, current_score):
    existing_awards = _matching_awards(client, settings, team_id)
    if team_state.award_id is None and existing_awards:
        team_state.award_id = existing_awards[0]["id"]

    matching_award = None
    for award in existing_awards:
        if _award_matches(award, current_score):
            matching_award = award
            break

    if matching_award is not None:
        team_state.award_id = matching_award["id"]
        for award in existing_awards:
            if award["id"] != matching_award["id"]:
                client.delete_award(award["id"])
        return

    changed = (
        team_state.award_id is None
        or client.get_award(team_state.award_id) is None
        or team_state.last_score != current_score["score"]
        or team_state.last_best_cycles != current_score["best_cycles"]
    )
    if not changed:
        for award in existing_awards:
            if award["id"] != team_state.award_id:
                client.delete_award(award["id"])
        return
    for award in existing_awards:
        client.delete_award(award["id"])
    if (
        team_state.award_id
        and team_state.award_id not in [award["id"] for award in existing_awards]
        and client.get_award(team_state.award_id) is not None
    ):
        client.delete_award(team_state.award_id)
    award = client.create_award(
        {
            "name": settings.award_name,
            "category": "watchdog-koth",
            "description": "Best watchdog run: {0} cycles".format(
                current_score["best_cycles"]
            ),
            "value": current_score["score"],
            "user_id": user_id,
            "team_id": team_id,
        }
    )
    team_state.award_id = award["id"]


def _sync_solve(client, settings, state, team_id, user_id, team_state):
    if not settings.solve_sync:
        if team_state.solve_id:
            if client.get_submission(team_state.solve_id) is not None:
                client.delete_submission(team_state.solve_id)
            team_state.solve_id = None
        return
    if team_state.solve_id and client.get_submission(team_state.solve_id) is not None:
        return
    for solve in client.list_team_solves(team_id):
        challenge_id = solve.get("challenge_id")
        challenge = solve.get("challenge") or {}
        if challenge_id == state.challenge_id or challenge.get("id") == state.challenge_id:
            team_state.solve_id = solve["id"]
            return
    submission = client.create_submission(
        {
            "challenge_id": state.challenge_id,
            "user_id": user_id,
            "team_id": team_id,
            "ip": "127.0.0.1",
            "provided": "watchdog-koth",
            "type": "incorrect",
        }
    )
    solved = client.promote_submission_to_solve(submission["id"])
    team_state.solve_id = solved["id"]


def sync_scores(client, settings, state, runs):
    state.ctfd_url = settings.ctfd_url
    ensure_challenge(client, settings, state)
    teams = _teams_by_id(client)
    scores = compute_scores(runs, settings.max_points, settings.min_points)

    for team_id, current_score in scores.items():
        team = teams.get(int(team_id))
        if team is None:
            raise ValueError("team_id {0} does not exist in CTFd".format(team_id))
        user_id = _carrier_user_id(client, team_id)
        if user_id is None:
            raise ValueError("team_id {0} has no members".format(team_id))
        team_state = state.team(team_id)
        _sync_award(client, settings, team_id, user_id, team_state, current_score)
        _sync_solve(client, settings, state, team_id, user_id, team_state)
        team_state.last_score = current_score["score"]
        team_state.last_best_cycles = current_score["best_cycles"]

    for team_id in list(state.teams.keys()):
        if int(team_id) not in scores:
            _delete_team_artifacts(client, state.teams[team_id])

    return {
        "challenge_id": state.challenge_id,
        "scored_teams": len(scores),
        "scores": scores,
    }
