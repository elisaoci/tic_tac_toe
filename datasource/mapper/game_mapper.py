import uuid
from domain.model.game import Game
from domain.model.board import Board
from datasource.model.game_datasource import GameDatasource

def to_datasource(game: Game) -> GameDatasource:
    return GameDatasource(
        uuid=uuid.UUID(game.uuid),
        field=[row[:] for row in game.board.field],
        current_player=game.board.current_player
    )

def to_domain(ds: GameDatasource) -> Game:
    board = Board()
    board.field = [row[:] for row in ds.field]
    board.current_player = ds.current_player
    game = Game(board=board)
    game.uuid = str(ds.uuid)
    return game