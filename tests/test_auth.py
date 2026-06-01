import allure


@allure.feature("Авторизация (Auth API)")
class TestAuth:

    @allure.title("TC_AUTH_001: Получение токена с валидными данными")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_token_valid_credentials(self, auth_client, test_data):
        with allure.step("POST /auth с admin/password123"):
            creds = test_data["valid_credentials"]
            auth_client.create_token(creds["username"], creds["password"], expected_status=200)

        with allure.step("Проверка наличия токена в ответе"):
            body = auth_client.json
            assert "token" in body
            assert body["token"] != "Bad credentials"
            assert len(body["token"]) > 0

    @allure.title("TC_AUTH_002: Получение токена с неверным паролем — токен не работает для защищённых запросов")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_token_wrong_password(self, auth_client, booking_client, test_data, created_booking):
        with allure.step("POST /auth с admin/wrongpass"):
            creds = test_data["invalid_credentials"]
            auth_client.create_token(creds["username"], creds["password"], expected_status=200)

        with allure.step("Получение токена из ответа (ожидается 'Bad credentials')"):
            bad_token = auth_client.json.get("token")

        with allure.step("Попытка обновить бронь с невалидным токеном — ожидаем 403"):
            booking_id = created_booking["bookingid"]
            booking_client.update_booking(
                booking_id, test_data["updated_booking"], bad_token, expected_status=403
            )

    @allure.title("TC_AUTH_003: Получение токена с несуществующим пользователем — токен невалиден")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_token_fake_user(self, auth_client, booking_client, test_data, created_booking):
        with allure.step("POST /auth с fakeuser/password123"):
            creds = test_data["fake_user_credentials"]
            auth_client.create_token(creds["username"], creds["password"], expected_status=200)

        with allure.step("Получение токена из ответа (ожидается 'Bad credentials')"):
            bad_token = auth_client.json.get("token")

        with allure.step("Попытка обновить бронь с невалидным токеном — ожидаем 403"):
            booking_id = created_booking["bookingid"]
            booking_client.update_booking(
                booking_id, test_data["updated_booking"], bad_token, expected_status=403
            )

    @allure.title("TC_AUTH_004: Использование токена для защищённого запроса — PUT /booking/{id} → 200")
    @allure.severity(allure.severity_level.NORMAL)
    def test_valid_token_for_protected_request(self, booking_client, test_data, auth_token, created_booking):
        with allure.step("PUT /booking/{id} с правильным токеном"):
            booking_id = created_booking["bookingid"]
            booking_client.update_booking(
                booking_id, test_data["updated_booking"], auth_token, expected_status=200
            )

        with allure.step("Проверка обновления данных"):
            data = booking_client.json
            assert data["firstname"] == test_data["updated_booking"]["firstname"]
            assert data["lastname"] == test_data["updated_booking"]["lastname"]
            assert data["totalprice"] == test_data["updated_booking"]["totalprice"]

    @allure.title("TC_AUTH_005: Использование неверного токена — PUT /booking/{id} → 403")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_invalid_token_rejected(self, booking_client, test_data, created_booking):
        with allure.step("PUT /booking/{id} с Cookie: token=invalid"):
            booking_id = created_booking["bookingid"]
            booking_client.update_booking(
                booking_id, test_data["updated_booking"], "invalid", expected_status=403
            )

    @allure.title("TC_AUTH_006: Запрос без токена к защищённому эндпоинту — PUT /booking/{id} → 403")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_no_token_for_protected_request(self, booking_client, test_data, created_booking):
        with allure.step("PUT /booking/{id} без заголовка Cookie"):
            booking_id = created_booking["bookingid"]
            booking_client.put(
                f"/booking/{booking_id}", json=test_data["updated_booking"], expected_status=403
            )

    @allure.title("TC_AUTH_007: Валидация формата токена — строка, не пустая")
    @allure.severity(allure.severity_level.MINOR)
    def test_token_format_is_valid_string(self, auth_client, test_data):
        with allure.step("POST /auth с валидными данными"):
            creds = test_data["valid_credentials"]
            auth_client.create_token(creds["username"], creds["password"], expected_status=200)

        with allure.step("Проверка формата токена: isinstance(str) и len > 0"):
            token = auth_client.json["token"]
            assert isinstance(token, str)
            assert len(token) > 0
            assert token != "Bad credentials"

    @allure.title("TC_AUTH_008: Повторное получение токена — оба токена валидны (идемпотентность)")
    @allure.severity(allure.severity_level.MINOR)
    def test_token_idempotency(self, auth_client, booking_client, test_data, created_booking):
        creds = test_data["valid_credentials"]

        with allure.step("Первый POST /auth — получение токена 1"):
            auth_client.create_token(creds["username"], creds["password"], expected_status=200)
            token1 = auth_client.json["token"]
            assert token1 != "Bad credentials"

        with allure.step("Второй POST /auth — получение токена 2"):
            auth_client.create_token(creds["username"], creds["password"], expected_status=200)
            token2 = auth_client.json["token"]
            assert token2 != "Bad credentials"

        with allure.step("Оба токена работают для защищённых запросов"):
            booking_id = created_booking["bookingid"]

            booking_client.update_booking(
                booking_id, test_data["updated_booking"], token1, expected_status=200
            )

            booking_client.update_booking(
                booking_id, test_data["valid_booking"], token2, expected_status=200
            )
