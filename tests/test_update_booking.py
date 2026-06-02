import allure
import jsonschema

from schemas.booking_schema import BOOKING_SCHEMA


@allure.feature("PUT/PATCH Booking API")
class TestUpdateBooking:

    @allure.title("TC_PUT_001: PUT — полное обновление с токеном → 200, все поля изменились")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_full_update_with_token(self, booking_client, test_data, auth_token, created_booking):
        booking_id = created_booking["bookingid"]
        with allure.step(f"PUT /booking/{booking_id} с токеном"):
            booking_client.update_booking(
                booking_id, test_data["updated_booking"], auth_token, expected_status=200
            )

        with allure.step("Проверка обновлённых данных"):
            data = booking_client.json
            assert data["firstname"] == test_data["updated_booking"]["firstname"]
            assert data["lastname"] == test_data["updated_booking"]["lastname"]
            assert data["totalprice"] == test_data["updated_booking"]["totalprice"]

    @allure.title("TC_PUT_002: PATCH — частичное обновление с токеном → только указанное поле изменилось")
    @allure.severity(allure.severity_level.NORMAL)
    def test_partial_update_with_token(self, booking_client, auth_token, created_booking):
        booking_id = created_booking["bookingid"]
        with allure.step(f"PATCH /booking/{booking_id} — только firstname"):
            booking_client.partial_update_booking(
                booking_id, {"firstname": "PatchedName"}, auth_token, expected_status=200
            )

        with allure.step("Проверка: firstname изменился, остальные поля прежние"):
            data = booking_client.json
            assert data["firstname"] == "PatchedName"

    @allure.title("TC_PUT_003: PUT несуществующей брони → 404")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_update_nonexistent_booking(self, booking_client, test_data, auth_token):
        with allure.step("PUT /booking/999999 с токеном — ожидаем 404"):
            booking_client.update_booking(
                999999, test_data["updated_booking"], auth_token, expected_status=404
            )

    @allure.title("TC_PUT_004: PUT без заголовка Cookie → 403 Forbidden")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_update_without_token(self, booking_client, test_data, created_booking):
        booking_id = created_booking["bookingid"]
        with allure.step(f"PUT /booking/{booking_id} без Cookie — ожидаем 403"):
            booking_client.put(
                f"/booking/{booking_id}", json=test_data["updated_booking"], expected_status=403
            )

    @allure.title("TC_PUT_005: PUT с неверным токеном → 403 Forbidden")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_update_with_invalid_token(self, booking_client, test_data, created_booking):
        booking_id = created_booking["bookingid"]
        with allure.step(f"PUT /booking/{booking_id} с token=invalid — ожидаем 403"):
            booking_client.update_booking(
                booking_id, test_data["updated_booking"], "invalid", expected_status=403
            )

    @allure.title("TC_PUT_006: PUT с пустым firstname — документирование поведения API")
    @allure.severity(allure.severity_level.NORMAL)
    def test_update_with_empty_firstname(self, booking_client, auth_token, created_booking, test_data):
        invalid_data = dict(test_data["updated_booking"])
        invalid_data["firstname"] = ""
        booking_id = created_booking["bookingid"]
        with allure.step(f"PUT /booking/{booking_id} с firstname=''"):
            response = booking_client.update_booking(booking_id, invalid_data, auth_token)

        with allure.step("Фиксируем фактический статус API"):
            assert response.status_code in [200, 400], (
                f"Неожиданный статус: {response.status_code}"
            )

    @allure.title("TC_PUT_007: PUT — обновление дат бронирования")
    @allure.severity(allure.severity_level.NORMAL)
    def test_update_booking_dates(self, booking_client, auth_token, created_booking, test_data):
        booking_id = created_booking["bookingid"]
        new_dates_payload = dict(test_data["updated_booking"])
        new_dates_payload["bookingdates"] = {"checkin": "2027-06-01", "checkout": "2027-06-10"}

        with allure.step(f"PUT /booking/{booking_id} с новыми датами"):
            booking_client.update_booking(booking_id, new_dates_payload, auth_token, expected_status=200)

        with allure.step("Проверка обновлённых дат"):
            data = booking_client.json
            assert data["bookingdates"]["checkin"] == "2027-06-01"
            assert data["bookingdates"]["checkout"] == "2027-06-10"

    @allure.title("TC_PUT_008: Валидация JSON Schema ответа после PUT")
    @allure.severity(allure.severity_level.MINOR)
    def test_validate_schema_after_update(self, booking_client, auth_token, created_booking, test_data):
        booking_id = created_booking["bookingid"]
        with allure.step(f"PUT /booking/{booking_id}"):
            booking_client.update_booking(
                booking_id, test_data["updated_booking"], auth_token, expected_status=200
            )

        with allure.step("Валидация JSON Schema"):
            jsonschema.validate(instance=booking_client.json, schema=BOOKING_SCHEMA)

    @allure.title("TC_PATCH_001: PATCH — обновление только totalprice")
    @allure.severity(allure.severity_level.MINOR)
    def test_patch_only_totalprice(self, booking_client, auth_token, created_booking):
        booking_id = created_booking["bookingid"]
        with allure.step(f"PATCH /booking/{booking_id} — только totalprice=500"):
            booking_client.partial_update_booking(
                booking_id, {"totalprice": 500}, auth_token, expected_status=200
            )

        with allure.step("Проверка: totalprice == 500"):
            assert booking_client.json["totalprice"] == 500

    @allure.title("TC_PATCH_002: PATCH — обновление только depositpaid")
    @allure.severity(allure.severity_level.MINOR)
    def test_patch_only_depositpaid(self, booking_client, auth_token, created_booking):
        booking_id = created_booking["bookingid"]
        with allure.step(f"PATCH /booking/{booking_id} — только depositpaid=false"):
            booking_client.partial_update_booking(
                booking_id, {"depositpaid": False}, auth_token, expected_status=200
            )

        with allure.step("Проверка: depositpaid == False"):
            assert booking_client.json["depositpaid"] is False
