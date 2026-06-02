import json
import pytest
from pathlib import Path
from api_client.auth_api import AuthAPI
from api_client.booking_api import BookingAPI


@pytest.fixture(scope="session")
def test_data():
    data_path = Path(__file__).parent / "data" / "test_data.json"
    with open(data_path) as f:
        return json.load(f)


@pytest.fixture(scope="session")
def auth_client():
    return AuthAPI()


@pytest.fixture(scope="session")
def booking_client():
    return BookingAPI()


@pytest.fixture(scope="session")
def auth_token(auth_client, test_data):
    creds = test_data["valid_credentials"]
    auth_client.create_token(creds["username"], creds["password"], expected_status=200)
    token = auth_client.json["token"]
    assert token != "Bad credentials"
    return token


@pytest.fixture
def created_booking(booking_client, test_data, auth_token):
    booking_client.create_booking(test_data["valid_booking"], expected_status=200)
    data = booking_client.json
    yield data
    booking_client.delete_booking(data["bookingid"], auth_token)
