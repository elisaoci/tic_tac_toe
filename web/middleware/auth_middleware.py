from functools import wraps
from flask import request, jsonify, make_response
import base64
from di.container import Container

container = Container()
user_service = container.user_service


def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        # СЦЕНАРИЙ 1: Пароль вообще не был введен (нажали "Отменить")
        if not auth_header:
            # Если запрос от браузера, отдаем красивую HTML страницу
            if 'text/html' in request.headers.get('Accept', ''):
                html = '''
                <h1>Доступ запрещен</h1>
                <p>Вы отменили вход или не авторизованы.</p>
                <p><a href="/register_page">Зарегистрироваться</a> | <a href="/">На главную</a></p>
                '''
                resp = make_response(html, 401)
                resp.headers['WWW-Authenticate'] = 'Basic realm="TicTacToe"'
                return resp

            # Если запрос от скрипта/API, отдаем JSON
            response = jsonify({"error": "Требуется авторизация"})
            response.status_code = 401
            response.headers['WWW-Authenticate'] = 'Basic realm="TicTacToe"'
            return response

        # Попытка расшифровать логин и пароль
        try:
            base64_credentials = auth_header.split(' ')[1]
            credentials = base64.b64decode(base64_credentials).decode('utf-8')
            login, password = credentials.split(':', 1)
        except Exception:
            return jsonify({"error": "Неверный формат заголовка Authorization"}), 401

        # Проверка пароля в базе данных
        uuid = user_service.authenticate(login, password)

        # СЦЕНАРИЙ 2: Пароль введен, но он неверный
        if not uuid:
            # Если запрос от браузера, отдаем красивую HTML страницу
            if 'text/html' in request.headers.get('Accept', ''):
                html = '''
                <h1>Неверный логин или пароль</h1>
                <p>Пожалуйста, попробуйте еще раз или создайте новый аккаунт.</p>
                <p><a href="/register_page">Зарегистрироваться</a> | <a href="/">На главную</a></p>
                '''
                resp = make_response(html, 401)
                resp.headers['WWW-Authenticate'] = 'Basic realm="TicTacToe"'
                return resp

            # Если запрос от скрипта/API, отдаем JSON
            response = jsonify({"error": "Неверный логин или пароль"})
            response.status_code = 401
            response.headers['WWW-Authenticate'] = 'Basic realm="TicTacToe"'
            return response

        # Если всё хорошо, сохраняем UUID пользователя и пропускаем дальше
        request.user_uuid = uuid
        return f(*args, **kwargs)

    return decorated_function