import allure


@allure.feature("DELETE Booking API")
class TestDeleteBooking:

    @allure.title("TC_DEL_001: DELETE с токеном → 201 Created")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_existing_booking_with_token(self, booking_client, test_data, auth_token):
        with allure.step("Создание брони для удаления"):
            booking_client.create_booking(test_data["valid_booking"], expected_status=200)
            booking_id = booking_client.json["bookingid"]

        with allure.step(f"DELETE /booking/{booking_id} с токеном — ожидаем 201"):
            booking_client.delete_booking(booking_id, auth_token, expected_status=201)

    @allure.title("TC_DEL_002: После DELETE бронь недоступна — GET → 404")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_deleted_booking_not_accessible(self, booking_client, test_data, auth_token):
        with allure.step("Создание брони"):
            booking_client.create_booking(test_data["valid_booking"], expected_status=200)
            booking_id = booking_client.json["bookingid"]

        with allure.step(f"DELETE /booking/{booking_id}"):
            booking_client.delete_booking(booking_id, auth_token, expected_status=201)

        with allure.step(f"GET /booking/{booking_id} — ожидаем 404"):
            booking_client.get_booking(booking_id, expected_status=404)

    @allure.title("TC_DEL_003: DELETE несуществующей брони → 404")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_nonexistent_booking(self, booking_client, auth_token):
        with allure.step("DELETE /booking/999999 с токеном — ожидаем 404"):
            booking_client.delete_booking(999999, auth_token, expected_status=404)

    @allure.title("TC_DEL_004: DELETE без токена → 403 Forbidden")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_without_token(self, booking_client, test_data, auth_token):
        with allure.step("Создание брони"):
            booking_client.create_booking(test_data["valid_booking"], expected_status=200)
            booking_id = booking_client.json["bookingid"]

        with allure.step(f"DELETE /booking/{booking_id} без Cookie — ожидаем 403"):
            booking_client.delete(f"/booking/{booking_id}", expected_status=403)

        with allure.step("Очистка"):
            booking_client.delete_booking(booking_id, auth_token)

    @allure.title("TC_DEL_005: DELETE с неверным токеном → 403 Forbidden")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_with_invalid_token(self, booking_client, test_data, auth_token):
        with allure.step("Создание брони"):
            booking_client.create_booking(test_data["valid_booking"], expected_status=200)
            booking_id = booking_client.json["bookingid"]

        with allure.step(f"DELETE /booking/{booking_id} с token=invalid — ожидаем 403"):
            booking_client.delete_booking(booking_id, "invalid", expected_status=403)

        with allure.step("Очистка"):
            booking_client.delete_booking(booking_id, auth_token)

    @allure.title("TC_DEL_006: Повторное удаление — первый раз 201, второй раз 404")
    @allure.severity(allure.severity_level.MINOR)
    def test_double_delete(self, booking_client, test_data, auth_token):
        with allure.step("Создание брони"):
            booking_client.create_booking(test_data["valid_booking"], expected_status=200)
            booking_id = booking_client.json["bookingid"]

        with allure.step("Первое удаление — ожидаем 201"):
            booking_client.delete_booking(booking_id, auth_token, expected_status=201)

        with allure.step("Второе удаление — ожидаем 404"):
            booking_client.delete_booking(booking_id, auth_token, expected_status=404)

    @allure.title("TC_DEL_007: Тело ответа DELETE — пустое или 'Created'")
    @allure.severity(allure.severity_level.MINOR)
    def test_delete_response_body(self, booking_client, test_data, auth_token):
        with allure.step("Создание брони"):
            booking_client.create_booking(test_data["valid_booking"], expected_status=200)
            booking_id = booking_client.json["bookingid"]

        with allure.step(f"DELETE /booking/{booking_id}"):
            response = booking_client.delete_booking(booking_id, auth_token, expected_status=201)

        with allure.step("Проверка тела ответа"):
            assert response.text in ["", "Created", "{}"]
