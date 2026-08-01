from functools import wraps
from flask import request, jsonify
import base64
from di.container import Container

container = Container()
user_service = container.user_service


def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            response = jsonify({"error": "Требуется авторизация"})
            response.status_code = 401
            response.headers['WWW-Authenticate'] = 'Basic realm="TicTacToe"'
            return response

        try:
            base64_credentials = auth_header.split(' ')[1]
            credentials = base64.b64decode(base64_credentials).decode('utf-8')
            login, password = credentials.split(':', 1)
        except Exception:
            return jsonify({"error": "Неверный формат заголовка Authorization"}), 401

        uuid = user_service.authenticate(login, password)

        if not uuid:
            response = jsonify({"error": "Неверный логин или пароль"})
            response.status_code = 401
            response.headers['WWW-Authenticate'] = 'Basic realm="TicTacToe"'
            return response

        request.user_uuid = uuid

        return f(*args, **kwargs)

    return decorated_function