import allure
import jsonschema
import pytest
import requests

from schemas.booking_schema import BOOKING_SCHEMA
from schemas.bookings_list_schema import BOOKINGS_LIST_SCHEMA


@allure.feature("Validation & Errors")
class TestValidation:

    @allure.title("TC_VAL_001: Валидация JSON Schema ответа GET /booking/{id}")
    @allure.severity(allure.severity_level.NORMAL)
    def test_booking_schema_validation(self, booking_client, created_booking):
        booking_id = created_booking["bookingid"]
        with allure.step(f"GET /booking/{booking_id}"):
            booking_client.get_booking(booking_id, expected_status=200)

        with allure.step("jsonschema.validate — схема BOOKING_SCHEMA"):
            jsonschema.validate(instance=booking_client.json, schema=BOOKING_SCHEMA)

    @allure.title("TC_VAL_002: Валидация JSON Schema ответа GET /booking (список)")
    @allure.severity(allure.severity_level.NORMAL)
    def test_bookings_list_schema_validation(self, booking_client):
        with allure.step("GET /booking"):
            booking_client.get_bookings(expected_status=200)

        with allure.step("jsonschema.validate — схема BOOKINGS_LIST_SCHEMA"):
            jsonschema.validate(instance=booking_client.json, schema=BOOKINGS_LIST_SCHEMA)

    @allure.title("TC_VAL_003: Content-Type всех ответов — application/json")
    @allure.severity(allure.severity_level.MINOR)
    def test_content_type_header(self, booking_client, created_booking):
        booking_id = created_booking["bookingid"]
        with allure.step("GET /booking"):
            r_list = booking_client.get_bookings(expected_status=200)
        with allure.step(f"GET /booking/{booking_id}"):
            r_single = booking_client.get_booking(booking_id, expected_status=200)

        with allure.step("Оба ответа имеют Content-Type: application/json"):
            assert "application/json" in r_list.headers.get("Content-Type", "")
            assert "application/json" in r_single.headers.get("Content-Type", "")

    @allure.title("TC_VAL_004: Время ответа всех эндпоинтов < 2000 мс")
    @allure.severity(allure.severity_level.MINOR)
    def test_response_time_all_endpoints(self, booking_client, created_booking):
        booking_id = created_booking["bookingid"]
        with allure.step("GET /booking"):
            r_list = booking_client.get_bookings(expected_status=200)
        with allure.step(f"GET /booking/{booking_id}"):
            r_single = booking_client.get_booking(booking_id, expected_status=200)

        with allure.step("Проверка elapsed < 2.0с"):
            assert r_list.elapsed.total_seconds() < 2.0, "GET /booking превысил 2с"
            assert r_single.elapsed.total_seconds() < 2.0, f"GET /booking/{booking_id} превысил 2с"

    @allure.title("TC_ERR_001: Невалидный JSON в теле запроса — документирование поведения API")
    @allure.severity(allure.severity_level.NORMAL)
    def test_bad_request_invalid_json(self, booking_client):
        with allure.step("POST /booking с невалидным JSON"):
            response = booking_client.session.post(
                f"{booking_client.BASE_URL}/booking",
                data="not_valid_json_{{{{",
                headers={"Content-Type": "application/json"},
            )

        with allure.step("Фиксируем фактический статус API"):
            assert response.status_code in [200, 400, 500], (
                f"Неожиданный статус: {response.status_code}"
            )

    @allure.title("TC_ERR_002: PUT без токена → 403 Forbidden")
    @allure.severity(allure.severity_level.NORMAL)
    def test_forbidden_without_token(self, booking_client, test_data, created_booking):
        booking_id = created_booking["bookingid"]
        with allure.step(f"PUT /booking/{booking_id} без Cookie — ожидаем 403"):
            booking_client.put(
                f"/booking/{booking_id}",
                json=test_data["updated_booking"],
                expected_status=403,
            )

    @allure.title("TC_ERR_003: GET несуществующего ресурса → 404 Not Found")
    @allure.severity(allure.severity_level.NORMAL)
    def test_not_found(self, booking_client):
        with allure.step("GET /booking/999999 — ожидаем 404"):
            booking_client.get_booking(999999, expected_status=404)

    @allure.title("TC_ERR_004: Таймаут запроса — requests.exceptions.Timeout")
    @allure.severity(allure.severity_level.MINOR)
    def test_request_timeout(self):
        with allure.step("GET /booking с timeout=0.001 — ожидаем Timeout"):
            with pytest.raises(requests.exceptions.Timeout):
                requests.get(
                    "https://restful-booker.herokuapp.com/booking",
                    timeout=0.001,
                )
