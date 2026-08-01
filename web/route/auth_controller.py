from flask import Blueprint, request, jsonify, render_template
import base64
from di.container import Container

auth_bp = Blueprint('auth', __name__)

container = Container()
user_service = container.user_service


@auth_bp.route('/register', methods=['POST'])
def register():
    # 1. Пытаемся получить JSON (если запрос от тестового скрипта)
    data = request.get_json(silent=True)

    # 2. Если JSON нет, берем данные из HTML-формы
    if not data:
        data = {
            'login': request.form.get('login'),
            'password': request.form.get('password')
        }

    # 3. Проверка на пустые поля
    if not data or not data.get('login') or not data.get('password'):
        if request.form:
            return "Ошибка: не хватает логина или пароля. <a href='/register_page'>Попробовать снова</a>", 400
        return jsonify({"error": "Не хватает логина или пароля"}), 400

    login = data['login']
    password = data['password']

    # 4. Вызываем сервис регистрации
    success = user_service.register(login, password)

    if success:
        if request.form:
            return f'''
            <h2>✅ Регистрация успешна!</h2>
            <p>Пользователь <b>{login}</b> создан.</p>
            <p><a href="/game/new">Нажми здесь, чтобы войти и начать игру</a></p>
            ''', 200
        return jsonify({"message": "Успешная регистрация"}), 201
    else:
        if request.form:
            return f"Ошибка: Пользователь с логином <b>{login}</b> уже существует. <a href='/register_page'>Попробовать другой логин</a>", 400
        return jsonify({"error": "Пользователь с таким логином уже существует"}), 400


@auth_bp.route('/register_page')
def register_page():
    return render_template('register.html')


@auth_bp.route('/login', methods=['POST'])
def login():
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