from flask import Blueprint, request, jsonify, render_template
from uuid import UUID

from domain.model.game import Game
from domain.service.game_service import GameServiceImpl
from web.model.game_request import GameRequest
from web.model.game_response import GameResponse
from web.mapper.game_web_mapper import request_to_domain, domain_to_response
from di.container import Container

from web.middleware.auth_middleware import require_auth

game_bp = Blueprint('game', __name__)

container = Container()
game_service: GameServiceImpl = container.game_service

'''@game_bp.route('/game/<uuid_str>', methods=['POST'])
@require_auth
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

    current_game = game_service.repo.get(uuid_str)
    if current_game is None:
        return jsonify({"error": "Игра не найдена"}), 404

    if not game_service.check_player_move(current_game, new_game_state):
        return jsonify({"error": "Некорректный ход игрока"}), 400

    if game_service.is_game_over(current_game):
        return jsonify({"error": "Игра уже завершена"}), 400

    updated_game = game_service.get_computer_move(new_game_state)
    game_service.repo.save(updated_game)

    return jsonify(domain_to_response(updated_game).__dict__)'''


@game_bp.route('/game/<uuid_str>', methods=['POST'])
@require_auth
def make_move(uuid_str: str):
    # 1. Достаем существующую игру из базы
    current_game = game_service.repo.get(uuid_str)
    if not current_game:
        return jsonify({"error": "Игра не найдена"}), 404

    # 2. Получаем новое поле от клиента (после хода игрока)
    data = request.get_json()
    current_game.board.field = data['field']

    # 3. После хода игрока (X), очередь компьютера (O)
    current_game.board.current_player = 2

    # 4. КРИТИЧЕСКИ ВАЖНО: Сохраняем ход игрока в ЛЮБОМ случае
    # (даже если это последний ход, приводящий к ничьей или победе)
    game_service.repo.save(current_game)

    # 5. Делаем ход компьютера ТОЛЬКО если игра ещё не закончена
    if not current_game.board.get_winner() and not current_game.board.is_fill():
        updated_game = game_service.get_computer_move(current_game)
    else:
        # Игра закончена (победа игрока или ничья) — компьютер не ходит
        updated_game = current_game

    # 6. Возвращаем клиенту обновленное состояние
    return jsonify({
        "uuid": updated_game.uuid,
        "field": updated_game.board.field,
        "current_player": updated_game.board.current_player
    })

@game_bp.route('/game/new')
@require_auth
def new_game_page():
    game = Game(user_uuid=request.user_uuid)
    container.repository.save(game)

    return render_template('game.html', game_uuid=game.uuid, board=game.board.field)


@game_bp.route('/game/<uuid_str>')
@require_auth
def game_page(uuid_str: str):
    try:
        UUID(uuid_str)
    except ValueError:
        return "Неверный UUID", 400

    game = container.repository.get(uuid_str)
    if not game:
        return "Игра не найдена", 404

    # 1. Определяем, есть ли победитель
    winner = game.board.get_winner()

    # 2. Если победителя нет, но поле заполнено — это ничья
    if winner is None and game.board.is_fill():
        winner = 0

        # 3. Возвращаем UUID, поле И статус победителя
    return render_template(
        'game.html',
        game_uuid=game.uuid,
        board=game.board.field,
        winner=winner  # <-- ЭТОЙ СТРОКИ НЕ ХВАТАЛО!
    )