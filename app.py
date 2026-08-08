from flask import Flask
from web.route.game_controller import game_bp
from web.route.auth_controller import auth_bp
from di.container import Container

def create_app() -> Flask:
    app = Flask(__name__, template_folder='templates', static_folder='static')

    app.register_blueprint(game_bp)
    app.register_blueprint(auth_bp)

    @app.route("/")
    def index():
        return '''
        <h1>Крестики-нолики</h1>
        <p><a href="/register_page"> Зарегистрировать нового пользователя</a></p>
        <p><a href="/games/new"> Начать игру (выбор режима)</a></p>
        <p><a href="/games/lobby"> Лобби (список игр PvP)</a></p>
        <p><a href="/history"> История моих игр</a></p>
        '''

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5001)