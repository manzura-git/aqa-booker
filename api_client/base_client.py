import requests


class BaseClient:
    BASE_URL = "https://restful-booker.herokuapp.com"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

        self.response = None

    @property
    def json(self):
        return self.response.json()

    def _request(self, method, path, expected_status=None, **kwargs):
        self.response = self.session.request(method, f"{self.BASE_URL}{path}", **kwargs)
        if expected_status is not None:
            assert self.response.status_code == expected_status
        return self.response

    def get(self, path, expected_status=None, **kwargs):
        return self._request("GET", path, expected_status, **kwargs)

    def post(self, path, expected_status=None, **kwargs):
        return self._request("POST", path, expected_status, **kwargs)

    def put(self, path, expected_status=None, **kwargs):
        return self._request("PUT", path, expected_status, **kwargs)

    def patch(self, path, expected_status=None, **kwargs):
        return self._request("PATCH", path, expected_status, **kwargs)

    def delete(self, path, expected_status=None, **kwargs):
        return self._request("DELETE", path, expected_status, **kwargs)
=======

    def get(self, path, **kwargs):
        return self.session.get(f"{self.BASE_URL}{path}", **kwargs)

    def post(self, path, **kwargs):
        return self.session.post(f"{self.BASE_URL}{path}", **kwargs)

    def put(self, path, **kwargs):
        return self.session.put(f"{self.BASE_URL}{path}", **kwargs)

    def patch(self, path, **kwargs):
        return self.session.patch(f"{self.BASE_URL}{path}", **kwargs)

    def delete(self, path, **kwargs):
        return self.session.delete(f"{self.BASE_URL}{path}", **kwargs)
