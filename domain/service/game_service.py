from domain.model.game import Game
from domain.service.game_service_interface import GameService
from datasource.repository.game_repository import GameRepository
from helpers.minimax import get_best_move

class GameServiceImpl(GameService):
    def __init__(self, repository: GameRepository):
        self.repo = repository

    def get_computer_move(self, game: Game) -> Game:
        if game.board.get_winner() or game.board.is_fill():
            return game

        row, col = get_best_move(game.board) # !!! а что если вернет ошибку (переписать)
        game.board.make_move(row, col)
        self.repo.save(game)
        return game

    def check_player_move(self, old_game: Game, new_game: Game) -> bool:
        if old_game.uuid != new_game.uuid:
            return False

        old_board = old_game.board
        new_board = new_game.board

        diff_count = 0
        for r in range(3):
            for c in range(3):
                if old_board.field[r][c] != new_board.field[r][c]:
                    if old_board.field[r][c] == 0 and new_board.field[r][c] == 1:
                        diff_count += 1
                    else:
                        return False

        return diff_count == 1 and new_board.current_player == 2

    def is_game_over(self, game: Game) -> bool:
        return game.board.get_winner() is not None or game.board.is_fill()