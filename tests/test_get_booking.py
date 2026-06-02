import allure
import jsonschema

from schemas.booking_schema import BOOKING_SCHEMA
from schemas.bookings_list_schema import BOOKINGS_LIST_SCHEMA


@allure.feature("GET Booking API")
class TestGetBooking:

    @allure.title("TC_GET_001: Получение всех броней — список не пустой")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_all_bookings(self, booking_client):
        with allure.step("GET /booking без параметров"):
            booking_client.get_bookings(expected_status=200)

        with allure.step("Ответ — непустой список"):
            data = booking_client.json
            assert isinstance(data, list)
            assert len(data) > 0

    @allure.title("TC_GET_002: Фильтрация по firstname — бронь из фикстуры присутствует")
    @allure.severity(allure.severity_level.NORMAL)
    def test_filter_by_firstname(self, booking_client, test_data, created_booking):
        firstname = test_data["valid_booking"]["firstname"]
        with allure.step(f"GET /booking?firstname={firstname}"):
            booking_client.get_bookings(params={"firstname": firstname}, expected_status=200)

        with allure.step("Созданная бронь присутствует в ответе"):
            ids = [b["bookingid"] for b in booking_client.json]
            assert created_booking["bookingid"] in ids

    @allure.title("TC_GET_003: Фильтрация по lastname — бронь из фикстуры присутствует")
    @allure.severity(allure.severity_level.NORMAL)
    def test_filter_by_lastname(self, booking_client, test_data, created_booking):
        lastname = test_data["valid_booking"]["lastname"]
        with allure.step(f"GET /booking?lastname={lastname}"):
            booking_client.get_bookings(params={"lastname": lastname}, expected_status=200)

        with allure.step("Созданная бронь присутствует в ответе"):
            ids = [b["bookingid"] for b in booking_client.json]
            assert created_booking["bookingid"] in ids

    @allure.title("TC_GET_004: Фильтрация по датам checkin/checkout — ответ список")
    @allure.severity(allure.severity_level.NORMAL)
    def test_filter_by_dates(self, booking_client):
        with allure.step("GET /booking?checkin=2026-01-01&checkout=2026-01-10"):
            booking_client.get_bookings(
                params={"checkin": "2026-01-01", "checkout": "2026-01-10"},
                expected_status=200,
            )

        with allure.step("Ответ является списком"):
            assert isinstance(booking_client.json, list)

    @allure.title("TC_GET_005: Получение существующей брони по ID — данные корректны")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_existing_booking_by_id(self, booking_client, test_data, created_booking):
        booking_id = created_booking["bookingid"]
        with allure.step(f"GET /booking/{booking_id}"):
            booking_client.get_booking(booking_id, expected_status=200)

        with allure.step("Проверка данных брони"):
            data = booking_client.json
            assert data["firstname"] == test_data["valid_booking"]["firstname"]
            assert data["lastname"] == test_data["valid_booking"]["lastname"]
            assert data["totalprice"] == test_data["valid_booking"]["totalprice"]

    @allure.title("TC_GET_006: Получение несуществующей брони по ID → 404")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_nonexistent_booking(self, booking_client):
        with allure.step("GET /booking/999999 — ожидаем 404"):
            booking_client.get_booking(999999, expected_status=404)

    @allure.title("TC_GET_007: Валидация JSON Schema списка броней")
    @allure.severity(allure.severity_level.MINOR)
    def test_validate_bookings_list_schema(self, booking_client):
        with allure.step("GET /booking"):
            booking_client.get_bookings(expected_status=200)

        with allure.step("Валидация схемы"):
            jsonschema.validate(instance=booking_client.json, schema=BOOKINGS_LIST_SCHEMA)

    @allure.title("TC_GET_008: Валидация JSON Schema одной брони")
    @allure.severity(allure.severity_level.MINOR)
    def test_validate_single_booking_schema(self, booking_client, created_booking):
        booking_id = created_booking["bookingid"]
        with allure.step(f"GET /booking/{booking_id}"):
            booking_client.get_booking(booking_id, expected_status=200)

        with allure.step("Валидация схемы"):
            jsonschema.validate(instance=booking_client.json, schema=BOOKING_SCHEMA)

    @allure.title("TC_GET_009: Content-Type в заголовках ответа — application/json")
    @allure.severity(allure.severity_level.MINOR)
    def test_response_content_type(self, booking_client):
        with allure.step("GET /booking"):
            response = booking_client.get_bookings(expected_status=200)

        with allure.step("Проверка Content-Type"):
            assert "application/json" in response.headers.get("Content-Type", "")

    @allure.title("TC_GET_010: Время ответа GET /booking < 2000 мс")
    @allure.severity(allure.severity_level.MINOR)
    def test_response_time(self, booking_client):
        with allure.step("GET /booking и замер времени"):
            response = booking_client.get_bookings(expected_status=200)

        with allure.step("Проверка: elapsed < 2.0 сек"):
            elapsed = response.elapsed.total_seconds()
            assert elapsed < 2.0, f"Время ответа {elapsed:.2f}с превышает 2.0с"
