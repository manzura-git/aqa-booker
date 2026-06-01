from api_client.base_client import BaseClient


class AuthAPI(BaseClient):

    def create_token(self, username: str, password: str, **kwargs):
        return self.post("/auth", json={"username": username, "password": password}, **kwargs)

    def create_token(self, username: str, password: str):
        return self.post("/auth", json={"username": username, "password": password})
