from domain.model.game import Game
from domain.model.game_status import GameStatus
from domain.service.game_service_interface import GameService
from datasource.repository.game_repository import SQLAlchemyGameRepository
from helpers.minimax import get_best_move

COMPUTER_UUID = "00000000-0000-0000-0000-000000000000"


class GameServiceImpl(GameService):
    def __init__(self, repository: SQLAlchemyGameRepository):
        self.repo = repository

    def create_game(self, player_uuid: str, mode: str = "pve") -> Game:
        game = Game(
            user_uuid=player_uuid,
            mode=mode,
            player1_uuid=player_uuid,
            player1_symbol=1,
            current_player_uuid=player_uuid
        )

        if mode == "pve":
            game.player2_uuid = COMPUTER_UUID
            game.player2_symbol = 2
            game.status = GameStatus.IN_PROGRESS
        else:
            game.status = GameStatus.WAITING

        self.repo.save(game)
        return game

    def join_game(self, game_uuid: str, player_uuid: str) -> Game:
        game = self.repo.get(game_uuid)
        if not game:
            raise ValueError("Игра не найдена")
        if game.status != GameStatus.WAITING:
            raise ValueError("К этой игре нельзя присоединиться")

        if game.player1_uuid == player_uuid:
            raise ValueError("Вы уже являетесь создателем этой игры. Нельзя играть против себя!")

        if game.player2_uuid:
            raise ValueError("В этой игре уже есть второй игрок")

        game.player2_uuid = player_uuid
        game.player2_symbol = 2
        game.current_player_uuid = game.player1_uuid
        game.status = GameStatus.IN_PROGRESS

        self.repo.save(game)
        return game

    def make_move(self, game_uuid: str, player_uuid: str, field: list) -> Game:
        game = self.repo.get(game_uuid)
        if not game:
            raise ValueError("Игра не найдена")
        if game.is_finished():
            raise ValueError("Игра уже закончена")

        if game.status == GameStatus.WAITING:
            raise ValueError("Игра ещё не началась. Ждём второго игрока.")

        if game.mode == "pvp" and not game.is_players_turn(player_uuid):
            raise ValueError("Сейчас не ваш ход")

        move_row, move_col = None, None
        for r in range(3):
            for c in range(3):
                if game.board.field[r][c] != field[r][c]:
                    move_row, move_col = r, c
                    break
            if move_row is not None:
                break

        if move_row is None:
            raise ValueError("Ход не найден: поле не изменилось")

        if game.board.field[move_row][move_col] != 0:
            raise ValueError("Клетка уже занята")

        player_symbol = game.player1_symbol if player_uuid == game.player1_uuid else game.player2_symbol

        game.board.field[move_row][move_col] = player_symbol

        winner_symbol = game.board.get_winner()
        if winner_symbol:
            game.status = GameStatus.WIN
            if winner_symbol == game.player1_symbol:
                game.winner_uuid = str(game.player1_uuid)
            else:
                game.winner_uuid = str(game.player2_uuid)
        elif game.board.is_fill():
            game.status = GameStatus.DRAW
            game.winner_uuid = None
        else:
            game.switch_turn()

            if game.mode == "pve" and game.current_player_uuid == COMPUTER_UUID:
                game.board.current_player = game.player2_symbol

                row, col = get_best_move(game.board)
                game.board.field[row][col] = game.player2_symbol

                winner_symbol = game.board.get_winner()
                if winner_symbol:
                    game.status = GameStatus.WIN
                    if winner_symbol == game.player1_symbol:
                        game.winner_uuid = str(game.player1_uuid)
                    else:
                        game.winner_uuid = str(game.player2_uuid)
                elif game.board.is_fill():
                    game.status = GameStatus.DRAW
                    game.winner_uuid = None
                else:
                    game.switch_turn()

        self.repo.save(game)
        return game

    def get_game(self, game_uuid: str) -> Game:
        return self.repo.get(game_uuid)

    def get_available_games(self) -> list:
        return self.repo.get_waiting_games()

    def check_player_move(self, old_game: Game, new_field: list) -> bool:
        diff_count = 0
        for r in range(3):
            for c in range(3):
                if old_game.board.field[r][c] != new_field[r][c]:
                    if old_game.board.field[r][c] == 0 and new_field[r][c] != 0:
                        diff_count += 1
                    else:
                        return False
        return diff_count == 1

    def is_game_over(self, game: Game) -> bool:
        return game.is_finished()

    def get_finished_games_by_user(self, user_uuid: str) -> list:
        return self.repo.get_finished_games_by_user(user_uuid)

    def get_top_players(self, limit: int) -> list:
        return self.repo.get_top_players(limit)