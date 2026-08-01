import requests
import base64

BASE_URL = "http://127.0.0.1:5001"

def get_auth_header(login, password):
    credentials = f"{login}:{password}"
    token = base64.b64encode(credentials.encode()).decode()
    return {"Authorization": f"Basic {token}"}

def test_register_new_user():
    """Тест: Успешная регистрация нового пользователя"""
    response = requests.post(f"{BASE_URL}/register", json={
        "login": "pytest_user",
        "password": "testpass"
    })
    assert response.status_code == 201
    assert response.json()["message"] == "Успешная регистрация"

def test_register_duplicate():
    """Тест: Регистрация существующего пользователя должна вернуть 400"""
    # Сначала регистрируем
    requests.post(f"{BASE_URL}/register", json={"login": "dup_user", "password": "123"})
    # Пробуем еще раз
    response = requests.post(f"{BASE_URL}/register", json={"login": "dup_user", "password": "123"})
    assert response.status_code == 400

def test_access_without_auth():
    """Тест: Доступ к игре без пароля должен вернуть 401"""
    response = requests.get(f"{BASE_URL}/game/new")
    assert response.status_code == 401

def test_access_with_wrong_password():
    """Тест: Доступ с неверным паролем должен вернуть 401"""
    headers = get_auth_header("non_existent_user", "wrong_pass")
    response = requests.get(f"{BASE_URL}/game/new", headers=headers)
    assert response.status_code == 401