import allure


@allure.feature("E2E тесты")
class TestE2E:

    @allure.title("TC_E2E_001: Полный цикл бронирования — Auth → Create → Get → Update → Delete → Verify")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_full_booking_lifecycle(self, auth_client, booking_client, test_data):
        with allure.step("Шаг 1: Авторизация и получение токена"):
            creds = test_data["valid_credentials"]
            auth_response = auth_client.create_token(creds["username"], creds["password"])
            assert auth_response.status_code == 200
            token = auth_response.json()["token"]
            assert token != "Bad credentials"

        with allure.step("Шаг 2: Создание брони"):
            create_response = booking_client.create_booking(test_data["valid_booking"])
            assert create_response.status_code == 200
            create_data = create_response.json()
            assert "bookingid" in create_data
            booking_id = create_data["bookingid"]

        with allure.step("Шаг 3: Получение брони по ID"):
            get_response = booking_client.get_booking(booking_id)
            assert get_response.status_code == 200
            get_data = get_response.json()
            assert get_data["firstname"] == test_data["valid_booking"]["firstname"]
            assert get_data["lastname"] == test_data["valid_booking"]["lastname"]

        with allure.step("Шаг 4: Обновление брони (PUT)"):
            update_response = booking_client.update_booking(
                booking_id, test_data["updated_booking"], token
            )
            assert update_response.status_code == 200
            update_data = update_response.json()
            assert update_data["firstname"] == test_data["updated_booking"]["firstname"]
            assert update_data["totalprice"] == test_data["updated_booking"]["totalprice"]

        with allure.step("Шаг 5: Удаление брони"):
            delete_response = booking_client.delete_booking(booking_id, token)
            assert delete_response.status_code == 201

        with allure.step("Шаг 6: Проверка, что бронь недоступна после удаления"):
            verify_response = booking_client.get_booking(booking_id)
            assert verify_response.status_code == 404

    @allure.title("TC_E2E_002: Цепочка — Create → фильтр по firstname → Get по ID")
    @allure.severity(allure.severity_level.NORMAL)
    def test_create_filter_get_chain(self, booking_client, test_data, auth_token):
        with allure.step("Создание брони"):
            create_response = booking_client.create_booking(test_data["valid_booking"])
            assert create_response.status_code == 200
            booking_id = create_response.json()["bookingid"]

        with allure.step("Фильтрация броней по firstname"):
            firstname = test_data["valid_booking"]["firstname"]
            filter_response = booking_client.get_bookings(params={"firstname": firstname})
            assert filter_response.status_code == 200
            ids_in_response = [b["bookingid"] for b in filter_response.json()]
            assert booking_id in ids_in_response

        with allure.step("Получение брони по ID и проверка данных"):
            get_response = booking_client.get_booking(booking_id)
            assert get_response.status_code == 200
            data = get_response.json()
            assert data["firstname"] == test_data["valid_booking"]["firstname"]
            assert data["lastname"] == test_data["valid_booking"]["lastname"]

        with allure.step("Очистка тестовых данных"):
            booking_client.delete_booking(booking_id, auth_token)

    @allure.title("TC_E2E_003: Обработка ошибок — Create → Update без токена → проверка 403 и неизменности данных")
    @allure.severity(allure.severity_level.NORMAL)
    def test_error_handling_in_chain(self, booking_client, test_data, auth_token):
        with allure.step("Создание брони"):
            create_response = booking_client.create_booking(test_data["valid_booking"])
            assert create_response.status_code == 200
            booking_id = create_response.json()["bookingid"]

        with allure.step("Попытка обновить бронь без токена — ожидаем 403"):
            update_response = booking_client.put(
                f"/booking/{booking_id}", json=test_data["updated_booking"]
            )
            assert update_response.status_code == 403

        with allure.step("Проверка, что данные брони не изменились после неудачного обновления"):
            get_response = booking_client.get_booking(booking_id)
            assert get_response.status_code == 200
            data = get_response.json()
            assert data["firstname"] == test_data["valid_booking"]["firstname"]
            assert data["lastname"] == test_data["valid_booking"]["lastname"]

        with allure.step("Очистка тестовых данных"):
            booking_client.delete_booking(booking_id, auth_token)
