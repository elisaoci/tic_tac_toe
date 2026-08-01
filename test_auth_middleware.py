import requests
import base64

BASE_URL = "http://127.0.0.1:5001"


def test_without_auth():
    """Тест: запрос без авторизации должен вернуть 401"""
    print("=== Тест 1: Запрос без авторизации ===")
    response = requests.get(f"{BASE_URL}/game/new")
    print(f"Статус: {response.status_code}")
    print(f"Ответ: {response.text}")


def test_with_auth():
    """Тест: запрос с авторизацией должен пройти"""
    print("\n=== Тест 2: Запрос с авторизацией ===")

    # Сначала регистрируем пользователя
    register_data = {"login": "game_tester", "password": "test123"}
    requests.post(f"{BASE_URL}/register", json=register_data)

    # Кодируем логин и пароль
    credentials = "game_tester:test123"
    base64_creds = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')

    headers = {"Authorization": f"Basic {base64_creds}"}
    response = requests.get(f"{BASE_URL}/game/new", headers=headers)

    print(f"Статус: {response.status_code}")
    if response.status_code == 200:
        print("✅ Щит пропустил авторизованного пользователя!")
    else:
        print(f" Ошибка: {response.text}")


if __name__ == "__main__":
    test_without_auth()
    test_with_auth()