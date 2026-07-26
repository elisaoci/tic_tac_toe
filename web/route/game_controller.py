from flask import Blueprint, request, jsonify, render_template
from uuid import UUID

from domain.model.game import Game
from domain.service.game_service import GameServiceImpl
from web.model.game_request import GameRequest
from web.model.game_response import GameResponse
from web.mapper.game_web_mapper import request_to_domain, domain_to_response
from di.container import Container

game_bp = Blueprint('game', __name__)

container = Container()
game_service: GameServiceImpl = container.game_service

@game_bp.route('/game/<uuid_str>', methods=['POST'])
def make_move(uuid_str: str):
    try:
        UUID(uuid_str)
    except ValueError:
        return jsonify({"error": "Неверный UUID"}), 400

    data = request.get_json()
    if not data or 'field' not in data:
        return jsonify({"error": "Ожидается JSON с полем 'field'"}), 400

    if not isinstance(data['field'], list) or len(data['field']) != 3 \
            or any(len(row) != 3 for row in data['field']):
        return jsonify({"error": "Поле должно быть 3×3"}), 400

    client_request = GameRequest(uuid=uuid_str, field=data['field'])
    new_game_state = request_to_domain(client_request)

    current_game = game_service.repo.get(UUID(uuid_str))
    if current_game is None:
        return jsonify({"error": "Игра не найдена"}), 404

    if not game_service.check_player_move(current_game, new_game_state):
        return jsonify({"error": "Некорректный ход игрока"}), 400

    if game_service.is_game_over(current_game):
        return jsonify({"error": "Игра уже завершена"}), 400

    updated_game = game_service.get_computer_move(new_game_state)
    game_service.repo.save(updated_game)

    return jsonify(domain_to_response(updated_game).__dict__)

@game_bp.route('/game/new')
def new_game_page():
    game = Game()
    container.repository.save(game)
    return render_template(
        'game.html',
        uuid=game.uuid,
        board=game.board.field,
        winner=None
    )

@game_bp.route('/game/<uuid_str>')
def game_page(uuid_str: str):
    try:
        UUID(uuid_str)
    except ValueError:
        return "Неверный UUID", 400

    game = container.repository.get(UUID(uuid_str))
    if not game:
        return "Игра не найдена", 404

    winner = game.board.get_winner()
    if winner is None and game.board.is_fill():
        winner = 0  # ничья

    return render_template(
        'game.html',
        uuid=game.uuid,
        board=game.board.field,
        winner=winner
    )