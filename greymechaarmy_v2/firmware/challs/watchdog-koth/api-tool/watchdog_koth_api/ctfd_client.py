import json
from urllib import error, parse, request


class CtfdApiError(RuntimeError):
    pass


class CtfdClient:
    def __init__(self, base_url, token):
        if not token:
            raise ValueError("CTFd token is required")
        self.base_url = base_url.rstrip("/")
        self.token = token

    def _request(self, method, path, payload=None):
        url = self.base_url + path
        data = None
        headers = {
            "Authorization": "Token {0}".format(self.token),
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
        req = request.Request(url, data=data, headers=headers, method=method)
        try:
            with request.urlopen(req, timeout=15) as response:
                body = response.read().decode("utf-8")
        except error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            if exc.code == 404:
                return None
            raise CtfdApiError("{0} {1} failed: {2}".format(method, path, body))
        except error.URLError as exc:
            raise CtfdApiError("{0} {1} failed: {2}".format(method, path, exc))
        if not body:
            return {}
        parsed = json.loads(body)
        if parsed.get("success") is False:
            raise CtfdApiError("{0} {1} failed: {2}".format(method, path, parsed))
        return parsed.get("data", parsed)

    def _get_list(self, path, params=None):
        if params:
            path = path + "?" + parse.urlencode(params)
        data = self._request("GET", path)
        return data or []

    def list_challenges(self):
        return self._get_list("/api/v1/challenges")

    def create_challenge(self, payload):
        return self._request("POST", "/api/v1/challenges", payload)

    def update_challenge(self, challenge_id, payload):
        return self._request("PATCH", "/api/v1/challenges/{0}".format(challenge_id), payload)

    def list_teams(self):
        return self._get_list("/api/v1/teams")

    def list_team_members(self, team_id):
        return self._get_list("/api/v1/teams/{0}/members".format(team_id))

    def list_team_solves(self, team_id):
        return self._get_list("/api/v1/teams/{0}/solves".format(team_id))

    def list_team_awards(self, team_id):
        return self._get_list("/api/v1/teams/{0}/awards".format(team_id))

    def get_award(self, award_id):
        return self._request("GET", "/api/v1/awards/{0}".format(award_id))

    def create_award(self, payload):
        return self._request("POST", "/api/v1/awards", payload)

    def delete_award(self, award_id):
        self._request("DELETE", "/api/v1/awards/{0}".format(award_id))

    def get_submission(self, submission_id):
        return self._request("GET", "/api/v1/submissions/{0}".format(submission_id))

    def create_submission(self, payload):
        return self._request("POST", "/api/v1/submissions", payload)

    def promote_submission_to_solve(self, submission_id):
        return self._request(
            "PATCH",
            "/api/v1/submissions/{0}".format(submission_id),
            {"type": "correct"},
        )

    def delete_submission(self, submission_id):
        self._request("DELETE", "/api/v1/submissions/{0}".format(submission_id))
