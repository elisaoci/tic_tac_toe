import requests
import base64

BASE_URL = "http://localhost:5001"


def test_register():
    print("=== Тест 1: Регистрация ===")
    data = {"login": "test_user", "password": "secret123"}
    response = requests.post(f"{BASE_URL}/register", json=data)

    print(f"Статус: {response.status_code}")
    print(f"Заголовки ответа: {response.headers}")
    print(f"Текст ответа: '{response.text}'")  # ← Показываем сырой текст

    # Только если статус успешный, пробуем парсить JSON
    if response.status_code == 201:
        try:
            print(f"JSON: {response.json()}")
        except:
            print("Не удалось распарсить JSON")


def test_login_correct():
    print("\n=== Тест 2: Вход с правильным паролем ===")
    # Кодируем логин и пароль в base64
    credentials = "test_user:secret123"
    base64_creds = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

    headers = {"Authorization": f"Basic {base64_creds}"}
    response = requests.post(f"{BASE_URL}/login", headers=headers)

    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.json()}")


def test_login_wrong():
    print("\n=== Тест 3: Вход с неправильным паролем ===")
    credentials = "test_user:wrong_password"
    base64_creds = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

    headers = {"Authorization": f"Basic {base64_creds}"}
    response = requests.post(f"{BASE_URL}/login", headers=headers)

    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.json()}")


if __name__ == "__main__":
    test_register()
    test_login_correct()
    test_login_wrong()