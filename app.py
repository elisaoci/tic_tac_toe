from flask import Flask
from web.route.game_controller import game_bp
from di.container import Container

def create_app() -> Flask:
    app = Flask(__name__, template_folder='templates', static_folder='static')

    Container()

    app.register_blueprint(game_bp)

    @app.route("/")
    def index():
        return '''
        <h1>Крестики-нолики</h1>
        <p><a href="/game/new">Начать новую игру</a></p>
        '''

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)