from domain.model.game import Game
from domain.model.board import Board
from web.model.game_request import GameRequest
from web.model.game_response import GameResponse

def request_to_domain(req: GameRequest) -> Game:
    board = Board()
    board.field = [row[:] for row in req.field]
    count_x = sum(row.count(1) for row in req.field)
    count_o = sum(row.count(2) for row in req.field)
    board.current_player = 2 if count_x > count_o else 1
    game = Game(board=board)
    game.uuid = req.uuid
    return game

def domain_to_response(game: Game) -> GameResponse:
    winner = game.board.get_winner()
    if winner is None and game.board.is_fill():
        winner = 0
    return GameResponse(
        uuid=game.uuid,
        field=[row[:] for row in game.board.field],
        winner=winner,
        is_over=game.board.get_winner() is not None or game.board.is_fill()
    )