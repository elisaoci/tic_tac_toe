from flask import Blueprint, request, jsonify
import base64
from di.container import Container

auth_bp = Blueprint('auth', __name__)

container = Container()
user_service = container.user_service


@auth_bp.route('/register', methods=['POST'])
def register():
    """Эндпоинт для регистрации нового пользователя (принимает только JSON)"""
    data = request.get_json()

    if not data or 'login' not in data or 'password' not in data:
        return jsonify({"error": "Не хватает логина или пароля"}), 400

    success = user_service.register(data['login'], data['password'])

    if success:
        return jsonify({"message": "Успешная регистрация"}), 201
    else:
        return jsonify({"error": "Пользователь с таким логином уже существует"}), 400


@auth_bp.route('/login', methods=['POST'])
def login():
    """Эндпоинт для входа (авторизации)"""
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return jsonify({"error": "Отсутствует заголовок Authorization"}), 401

    try:
        base64_credentials = auth_header.split(' ')[1]
        credentials = base64.b64decode(base64_credentials).decode('utf-8')
        login, password = credentials.split(':', 1)
    except Exception:
        return jsonify({"error": "Неверный формат заголовка Authorization"}), 401

    uuid = user_service.authenticate(login, password)

    if uuid:
        return jsonify({"uuid": uuid}), 200
    else:
        return jsonify({"error": "Неверный логин или пароль"}), 401