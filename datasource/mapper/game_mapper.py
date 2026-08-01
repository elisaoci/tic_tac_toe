import uuid
from domain.model.game import Game
from domain.model.board import Board
from datasource.model.game_model import GameModel

def to_model(game: Game) -> GameModel:
    return GameModel(
        uuid=game.uuid,
        user_uuid=game.user_uuid,
        field=game.board.field,
        current_player=game.board.current_player
    )

def to_domain(model: GameModel) -> Game:
    board = Board()
    board.field = model.field
    board.current_player = model.current_player
    game = Game(board=board, user_uuid=model.user_uuid)
    game.uuid = model.uuid
    return game