from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from uuid import UUID

from domain.model.game import Game
from domain.model.game_status import GameStatus
from domain.service.game_service import GameServiceImpl
from di.container import Container
from web.middleware.auth_middleware import require_auth
from datasource.model.user_model import UserModel
from datasource.database import SessionLocal

game_bp = Blueprint('game', __name__)

container = Container()
game_service: GameServiceImpl = container.game_service


@game_bp.route('/game/<uuid_str>', methods=['POST'])
@require_auth
def make_move(uuid_str: str):
    """Обработка хода игрока (универсально для PvP и PvE)"""
    try:
        UUID(uuid_str)
    except ValueError:
        return jsonify({"error": "Неверный UUID"}), 400

    data = request.get_json()
    if not data or 'field' not in data:
        return jsonify({"error": "Ожидается JSON с полем 'field'"}), 400

    try:
        updated_game = game_service.make_move(
            game_uuid=uuid_str,
            player_uuid=request.user_uuid,
            field=data['field']
        )

        return jsonify({
            "uuid": updated_game.uuid,
            "field": updated_game.board.field,
            "status": updated_game.status.value,
            "current_player_uuid": updated_game.current_player_uuid
        })

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500


@game_bp.route('/games/new', methods=['GET', 'POST'])
@require_auth
def create_game_page():
    """Страница выбора режима игры"""
    if request.method == 'POST':
        mode = request.form.get('mode', 'pve')
        if mode not in ['pve', 'pvp']:
            mode = 'pve'

        game = game_service.create_game(player_uuid=request.user_uuid, mode=mode)
        return redirect(url_for('game.game_page', uuid_str=game.uuid))

    return render_template('create_game.html')


@game_bp.route('/game/new')
@require_auth
def new_game_redirect():
    """Старая ссылка для совместимости, перенаправляет на выбор режима"""
    return redirect(url_for('game.create_game_page'))


@game_bp.route('/game/<uuid_str>')
@require_auth
def game_page(uuid_str: str):
    """Отображение страницы конкретной игры"""
    try:
        UUID(uuid_str)
    except ValueError:
        return "Неверный UUID", 400

    game = game_service.get_game(uuid_str)
    if not game:
        return "Игра не найдена", 404

    # Маппинг статуса в winner для совместимости с frontend (game.html)
    winner = None
    if game.status == GameStatus.WIN:
        if game.get_winner_uuid() == game.player1_uuid:
            winner = 1
        elif game.get_winner_uuid() == game.player2_uuid:
            winner = 2
    elif game.status == GameStatus.DRAW:
        winner = 0

    # Определяем роли текущего пользователя в этой игре
    is_player1 = (request.user_uuid == game.player1_uuid)
    is_player2 = (request.user_uuid == game.player2_uuid)
    is_my_turn = (game.current_player_uuid == request.user_uuid)

    # Определяем символ текущего игрока (1 = X, 2 = O)
    my_symbol = 1 if is_player1 else 2  # <-- ВОТ ЭТА СТРОКА БЫЛА ПРОПУЩЕНА

    return render_template(
        'game.html',
        game_uuid=game.uuid,
        board=game.board.field,
        winner=winner,
        game_status=game.status.value,
        is_my_turn=is_my_turn,
        game_mode=game.mode,
        is_player1=is_player1,
        is_player2=is_player2,
        my_symbol=my_symbol
    )

# ==========================================================
# API ENDPOINT'Ы ДЛЯ МУЛЬТИПЛЕЕРА (ЗАДАНИЕ 3)
# ==========================================================

@game_bp.route('/games', methods=['POST'])
@require_auth
def create_game_api():
    """Создание новой игры через API"""
    data = request.get_json() or {}
    mode = data.get('mode', 'pve')

    if mode not in ['pve', 'pvp']:
        return jsonify({"error": "Неверный режим. Используйте 'pve' или 'pvp'"}), 400

    game = game_service.create_game(player_uuid=request.user_uuid, mode=mode)

    return jsonify({
        "uuid": game.uuid,
        "mode": game.mode,
        "status": game.status.value,
        "message": "Игра успешно создана"
    }), 201


@game_bp.route('/games', methods=['GET'])
@require_auth
def get_available_games_api():
    """Получение списка игр, ожидающих второго игрока (лобби PvP)"""
    games = game_service.get_available_games()

    return jsonify([{
        "uuid": g.uuid,
        "mode": g.mode,
        "status": g.status.value,
        "player1_uuid": g.player1_uuid
    } for g in games]), 200


@game_bp.route('/games/<uuid_str>/join', methods=['POST'])
@require_auth
def join_game_api(uuid_str: str):
    """Присоединение второго игрока к игре (только для PvP)"""
    try:
        game = game_service.join_game(game_uuid=uuid_str, player_uuid=request.user_uuid)

        # Если запрос НЕ является JSON (то есть пришел из обычной HTML-формы браузера)
        if not request.is_json:
            return redirect(url_for('game.game_page', uuid_str=uuid_str))

        # Если это API-запрос (например, из тестов или curl), возвращаем JSON
        return jsonify({
            "uuid": game.uuid,
            "status": game.status.value,
            "message": "Вы успешно присоединились к игре"
        }), 200

    except ValueError as e:
        if not request.is_json:
            return f"Ошибка: {str(e)}. <a href='/games/new'>Вернуться к выбору игр</a>", 400
        return jsonify({"error": str(e)}), 400

@game_bp.route('/games/lobby')
@require_auth
def lobby_page():
    """Страница лобби для выбора игры PvP"""
    games = game_service.get_available_games()
    return render_template('lobby.html', games=games)


@game_bp.route('/games/history', methods=['GET'])
@require_auth
def get_game_history():
    """Получение истории завершенных игр текущего пользователя"""
    games = game_service.get_finished_games_by_user(request.user_uuid)

    return jsonify([{
        "uuid": g.uuid,
        "mode": g.mode,
        "status": g.status.value,
        "created_at": g.created_at.isoformat() if g.created_at else None,
        "player1_uuid": g.player1_uuid,
        "player2_uuid": g.player2_uuid
    } for g in games]), 200

@game_bp.route('/history')
@require_auth
def history_page():
    """Страница просмотра истории игр"""
    games = game_service.get_finished_games_by_user(request.user_uuid)
    return render_template('history.html', games=games)


@game_bp.route('/leaderboard')
@require_auth
def leaderboard_page():
    """Страница таблицы лидеров"""
    n = request.args.get('n', 10, type=int)
    stats = game_service.get_top_players(n)

    # Создаём сессию для получения данных о пользователях
    session = SessionLocal()
    try:
        players = []
        for stat in stats:
            # Ищем пользователя в БД
            user = session.query(UserModel).filter(UserModel.uuid == stat['user_uuid']).first()
            login = user.login if user else "Unknown"

            players.append({
                "login": login,
                "wins": stat['total_wins'],
                "losses_draws": stat['total_losses_draws'],
                "win_ratio": round(stat['win_ratio'], 2)
            })
    finally:
        session.close()

    return render_template('leaderboard.html', players=players)