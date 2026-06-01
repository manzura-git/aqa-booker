import requests


class BaseClient:
    BASE_URL = "https://restful-booker.herokuapp.com"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

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
