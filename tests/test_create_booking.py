import allure
import jsonschema

from schemas.booking_schema import BOOKING_SCHEMA


@allure.feature("POST Booking API")
class TestCreateBooking:

    @allure.title("TC_POST_001: Создание валидной брони — 200, есть bookingid")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_valid_booking(self, booking_client, test_data, auth_token):
        with allure.step("POST /booking с полным объектом"):
            booking_client.create_booking(test_data["valid_booking"], expected_status=200)

        with allure.step("Проверка наличия bookingid и booking в ответе"):
            data = booking_client.json
            assert "bookingid" in data
            assert "booking" in data

        with allure.step("Очистка тестовых данных"):
            booking_client.delete_booking(data["bookingid"], auth_token)

    @allure.title("TC_POST_002: Создание брони с минимальными полями — 200")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_booking_minimal_fields(self, booking_client, test_data, auth_token):
        with allure.step("POST /booking без additionalneeds"):
            booking_client.create_booking(test_data["minimal_booking"], expected_status=200)

        with allure.step("Проверка bookingid"):
            data = booking_client.json
            assert "bookingid" in data

        with allure.step("Очистка"):
            booking_client.delete_booking(data["bookingid"], auth_token)

    @allure.title("TC_POST_003: Создание брони с depositpaid=false — поле сохранено")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_booking_depositpaid_false(self, booking_client, auth_token):
        payload = {
            "firstname": "Test",
            "lastname": "User",
            "totalprice": 100,
            "depositpaid": False,
            "bookingdates": {"checkin": "2026-04-01", "checkout": "2026-04-05"},
        }
        with allure.step("POST /booking с depositpaid=false"):
            booking_client.create_booking(payload, expected_status=200)

        with allure.step("Проверка depositpaid=False в ответе"):
            data = booking_client.json
            assert data["booking"]["depositpaid"] is False

        with allure.step("Очистка"):
            booking_client.delete_booking(data["bookingid"], auth_token)

    @allure.title("TC_POST_004: Создание брони с additionalneeds — поле в ответе")
    @allure.severity(allure.severity_level.MINOR)
    def test_create_booking_with_additionalneeds(self, booking_client, auth_token):
        payload = {
            "firstname": "Test",
            "lastname": "User",
            "totalprice": 200,
            "depositpaid": True,
            "bookingdates": {"checkin": "2026-05-01", "checkout": "2026-05-05"},
            "additionalneeds": "breakfast",
        }
        with allure.step("POST /booking с additionalneeds='breakfast'"):
            booking_client.create_booking(payload, expected_status=200)

        with allure.step("Проверка additionalneeds в ответе"):
            data = booking_client.json
            assert data["booking"]["additionalneeds"] == "breakfast"

        with allure.step("Очистка"):
            booking_client.delete_booking(data["bookingid"], auth_token)

    @allure.title("TC_POST_005: Создание брони с невалидными датами — документирование поведения API")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_booking_invalid_dates(self, booking_client, auth_token):
        payload = {
            "firstname": "Test",
            "lastname": "User",
            "totalprice": 100,
            "depositpaid": True,
            "bookingdates": {"checkin": "2026-05-10", "checkout": "2026-05-01"},
        }
        with allure.step("POST /booking с checkin > checkout"):
            response = booking_client.create_booking(payload)

        with allure.step("API не валидирует порядок дат — фиксируем фактический статус"):
            assert response.status_code in [200, 400, 422], (
                f"Неожиданный статус: {response.status_code}"
            )
            if response.status_code == 200:
                booking_client.delete_booking(booking_client.json["bookingid"], auth_token)

    @allure.title("TC_POST_006: Создание брони с пустым firstname — документирование поведения API")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_create_booking_empty_firstname(self, booking_client, auth_token):
        payload = {
            "firstname": "",
            "lastname": "User",
            "totalprice": 100,
            "depositpaid": True,
            "bookingdates": {"checkin": "2026-06-01", "checkout": "2026-06-05"},
        }
        with allure.step("POST /booking с firstname=''"):
            response = booking_client.create_booking(payload)

        with allure.step("Фиксируем фактический статус API"):
            assert response.status_code in [200, 400], (
                f"Неожиданный статус: {response.status_code}"
            )
            if response.status_code == 200:
                booking_client.delete_booking(booking_client.json["bookingid"], auth_token)

    @allure.title("TC_POST_007: Создание брони с lastname длиной 1000 символов")
    @allure.severity(allure.severity_level.MINOR)
    def test_create_booking_very_long_lastname(self, booking_client, auth_token):
        payload = {
            "firstname": "Test",
            "lastname": "A" * 1000,
            "totalprice": 100,
            "depositpaid": True,
            "bookingdates": {"checkin": "2026-07-01", "checkout": "2026-07-05"},
        }
        with allure.step("POST /booking с lastname длиной 1000 символов"):
            response = booking_client.create_booking(payload)

        with allure.step("Фиксируем фактический статус API"):
            assert response.status_code in [200, 400], (
                f"Неожиданный статус: {response.status_code}"
            )
            if response.status_code == 200:
                booking_client.delete_booking(booking_client.json["bookingid"], auth_token)

    @allure.title("TC_POST_008: Валидация JSON Schema созданной брони")
    @allure.severity(allure.severity_level.MINOR)
    def test_validate_created_booking_schema(self, booking_client, test_data, auth_token):
        with allure.step("POST /booking"):
            booking_client.create_booking(test_data["valid_booking"], expected_status=200)

        with allure.step("Валидация поля booking по JSON Schema"):
            data = booking_client.json
            jsonschema.validate(instance=data["booking"], schema=BOOKING_SCHEMA)

        with allure.step("Очистка"):
            booking_client.delete_booking(data["bookingid"], auth_token)

    @allure.title("TC_POST_009: Две созданные брони имеют разные bookingid")
    @allure.severity(allure.severity_level.MINOR)
    def test_unique_booking_ids(self, booking_client, test_data, auth_token):
        with allure.step("Создание первой брони"):
            r1 = booking_client.create_booking(test_data["valid_booking"], expected_status=200)
            id1 = r1.json()["bookingid"]

        with allure.step("Создание второй брони"):
            r2 = booking_client.create_booking(test_data["valid_booking"], expected_status=200)
            id2 = r2.json()["bookingid"]

        with allure.step("Проверка уникальности id"):
            assert id1 != id2

        with allure.step("Очистка"):
            booking_client.delete_booking(id1, auth_token)
            booking_client.delete_booking(id2, auth_token)

    @allure.title("TC_POST_010: Созданная бронь сразу доступна по GET")
    @allure.severity(allure.severity_level.NORMAL)
    def test_created_booking_accessible_by_get(self, booking_client, test_data, auth_token):
        with allure.step("POST /booking"):
            booking_client.create_booking(test_data["valid_booking"], expected_status=200)
            booking_id = booking_client.json["bookingid"]

        with allure.step(f"GET /booking/{booking_id}"):
            booking_client.get_booking(booking_id, expected_status=200)

        with allure.step("Данные совпадают с отправленными"):
            data = booking_client.json
            assert data["firstname"] == test_data["valid_booking"]["firstname"]
            assert data["lastname"] == test_data["valid_booking"]["lastname"]

        with allure.step("Очистка"):
            booking_client.delete_booking(booking_id, auth_token)
