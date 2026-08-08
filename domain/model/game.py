import uuid
from domain.model.board import Board
from domain.model.game_status import GameStatus
from datetime import datetime


class Game:
    """
    Модель текущей игры.
    Поддерживает два режима:
    - pve: игрок против компьютера (Minimax)
    - pvp: игрок против игрока
    """

    def __init__(
            self,
            board: Board = None,
            user_uuid: str = None,
            status: GameStatus = GameStatus.WAITING,
            mode: str = "pve",  # "pve" или "pvp"
            player1_uuid: str = None,
            player2_uuid: str = None,
            player1_symbol: int = 1,  # 1 = X (всегда ходит первым)
            player2_symbol: int = 2,  # 2 = O
            current_player_uuid: str = None,
            created_at: datetime = None
    ):
        self.uuid = str(uuid.uuid4())
        self.user_uuid = user_uuid  # UUID создателя игры
        self.status = status
        self.mode = mode

        # Игроки и их значки
        self.player1_uuid = player1_uuid
        self.player2_uuid = player2_uuid
        self.player1_symbol = player1_symbol
        self.player2_symbol = player2_symbol
        self.current_player_uuid = current_player_uuid

        # Игровое поле
        if board is None:
            self.board = Board()
        else:
            self.board = board

        self.created_at = created_at if created_at else datetime.utcnow()

    # === Вспомогательные методы ===

    def is_waiting(self) -> bool:
        """Игра ожидает второго игрока"""
        return self.status == GameStatus.WAITING and self.player2_uuid is None

    def is_in_progress(self) -> bool:
        """Игра идет"""
        return self.status == GameStatus.IN_PROGRESS

    def is_finished(self) -> bool:
        """Игра закончена (ничья или победа)"""
        return self.status in [GameStatus.DRAW, GameStatus.WIN]

    def get_winner_uuid(self) -> str:
        """Возвращает UUID победителя, если игра закончена победой"""
        if self.status != GameStatus.WIN:
            return None

        winner_symbol = self.board.get_winner()
        if winner_symbol == self.player1_symbol:
            return self.player1_uuid
        elif winner_symbol == self.player2_symbol:
            return self.player2_uuid
        return None

    def is_players_turn(self, player_uuid: str) -> bool:
        """Проверяет, является ли сейчас ход этого игрока"""
        return self.current_player_uuid == player_uuid

    def switch_turn(self):
        """Переключает ход на следующего игрока"""
        if self.current_player_uuid == self.player1_uuid:
            self.current_player_uuid = self.player2_uuid
        else:
            self.current_player_uuid = self.player1_uuid