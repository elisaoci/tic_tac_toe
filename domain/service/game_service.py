from domain.model.game import Game
from domain.model.game_status import GameStatus
from domain.service.game_service_interface import GameService
from datasource.repository.game_repository import SQLAlchemyGameRepository
from helpers.minimax import get_best_move

# Специальный UUID для компьютера, чтобы удовлетворить требования базы данных
COMPUTER_UUID = "00000000-0000-0000-0000-000000000000"


class GameServiceImpl(GameService):
    def __init__(self, repository: SQLAlchemyGameRepository):
        self.repo = repository

    def create_game(self, player_uuid: str, mode: str = "pve") -> Game:
        """Создание новой игры"""
        game = Game(
            user_uuid=player_uuid,
            mode=mode,
            player1_uuid=player_uuid,
            player1_symbol=1,  # Создатель всегда ходит крестиками (X)
            current_player_uuid=player_uuid
        )

        if mode == "pve":
            # Для PvE компьютер присоединяется сразу
            game.player2_uuid = COMPUTER_UUID
            game.player2_symbol = 2  # Компьютер ходит ноликами (O)
            game.status = GameStatus.IN_PROGRESS
        else:
            # Для PvP игра ждет второго игрока
            game.status = GameStatus.WAITING

        self.repo.save(game)
        return game

    def join_game(self, game_uuid: str, player_uuid: str) -> Game:
        """Присоединение второго игрока к игре (только для PvP)"""
        game = self.repo.get(game_uuid)
        if not game:
            raise ValueError("Игра не найдена")
        if game.status != GameStatus.WAITING:
            raise ValueError("К этой игре нельзя присоединиться")

        game.player2_uuid = player_uuid
        game.player2_symbol = 2  # Второй игрок ходит ноликами (O)
        game.current_player_uuid = game.player1_uuid  # Первым ходит создатель (X)
        game.status = GameStatus.IN_PROGRESS

        self.repo.save(game)
        return game

    def make_move(self, game_uuid: str, player_uuid: str, field: list) -> Game:
        """Обработка хода игрока (универсальный метод для PvP и PvE)"""
        game = self.repo.get(game_uuid)
        if not game:
            raise ValueError("Игра не найдена")
        if game.is_finished():
            raise ValueError("Игра уже закончена")

        # Для PvP проверяем, чей сейчас ход
        if game.mode == "pvp" and not game.is_players_turn(player_uuid):
            raise ValueError("Сейчас не ваш ход")

        # 1. Находим клетку, куда сходил игрок (сравниваем старое и новое поле)
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

        # 2. Проверяем, что игрок сходил в пустую клетку
        if game.board.field[move_row][move_col] != 0:
            raise ValueError("Клетка уже занята")

        # 3. Определяем символ игрока
        player_symbol = game.player1_symbol if player_uuid == game.player1_uuid else game.player2_symbol

        # 4. Ставим символ игрока вручную (без переключения current_player,
        #    потому что мы сами будем управлять очередностью)
        game.board.field[move_row][move_col] = player_symbol

        # 5. Проверяем, не привел ли ход к победе или ничьей
        winner_symbol = game.board.get_winner()
        if winner_symbol:
            game.status = GameStatus.WIN
        elif game.board.is_fill():
            game.status = GameStatus.DRAW
        else:
            # 6. Переключаем ход
            game.switch_turn()

            # 7. Если режим PvE и сейчас ход компьютера — делаем его
            if game.mode == "pve" and game.current_player_uuid == COMPUTER_UUID:
                # ВАЖНО: перед вызовом Minimax убеждаемся, что на доске
                # current_player = символ компьютера (O = 2)
                game.board.current_player = game.player2_symbol

                row, col = get_best_move(game.board)
                game.board.field[row][col] = game.player2_symbol

                # Проверяем состояние после хода компьютера
                winner_symbol = game.board.get_winner()
                if winner_symbol:
                    game.status = GameStatus.WIN
                elif game.board.is_fill():
                    game.status = GameStatus.DRAW
                else:
                    game.switch_turn()  # Возвращаем ход человеку

        self.repo.save(game)
        return game

    def get_game(self, game_uuid: str) -> Game:
        """Получить игру по UUID"""
        return self.repo.get(game_uuid)

    def get_available_games(self) -> list:
        """Получить список игр, ожидающих второго игрока (лобби PvP)"""
        return self.repo.get_waiting_games()

    def check_player_move(self, old_game: Game, new_field: list) -> bool:
        """Проверка валидности хода"""
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
        """Проверка окончания игры"""
        return game.is_finished()

    def get_finished_games_by_user(self, user_uuid: str) -> list:
        """Получить все завершенные игры пользователя"""
        return self.repo.get_finished_games_by_user(user_uuid)