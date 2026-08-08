from domain.model.game import Game
from domain.model.board import Board
from domain.model.game_status import GameStatus
from datasource.model.game_model import GameModel


def to_model(game: Game) -> GameModel:
    """Конвертирует Domain-модель в модель БД"""
    return GameModel(
        uuid=game.uuid,
        user_uuid=game.user_uuid,
        status=game.status,
        mode=game.mode,
        player1_uuid=game.player1_uuid,
        player2_uuid=game.player2_uuid,
        player1_symbol=game.player1_symbol,
        player2_symbol=game.player2_symbol,
        current_player_uuid=game.current_player_uuid,
        field=game.board.field,
        current_player=game.board.current_player,
        created_at = game.created_at if hasattr(game, 'created_at') else None
    )


def to_domain(model: GameModel) -> Game:
    """Конвертирует модель БД в Domain-модель"""
    board = Board()
    board.field = model.field
    board.current_player = model.current_player

    game = Game(
        board=board,
        user_uuid=str(model.user_uuid),
        status=model.status,
        mode=model.mode,
        player1_uuid=str(model.player1_uuid) if model.player1_uuid else None,
        player2_uuid=str(model.player2_uuid) if model.player2_uuid else None,
        player1_symbol=model.player1_symbol,
        player2_symbol=model.player2_symbol,
        current_player_uuid=str(model.current_player_uuid) if model.current_player_uuid else None
    )
    game.uuid = str(model.uuid)

    if hasattr(model, 'created_at'):
        game.created_at = model.created_at

    return game