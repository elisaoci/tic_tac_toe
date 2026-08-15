import uuid
from domain.model.board import Board
from domain.model.game_status import GameStatus
from datetime import datetime


class Game:
    def __init__(
            self,
            board: Board = None,
            user_uuid: str = None,
            status: GameStatus = GameStatus.WAITING,
            mode: str = "pve",
            player1_uuid: str = None,
            player2_uuid: str = None,
            player1_symbol: int = 1,
            player2_symbol: int = 2,
            current_player_uuid: str = None,
            winner_uuid: str = None,
            created_at: datetime = None
    ):
        self.uuid = str(uuid.uuid4())
        self.user_uuid = user_uuid
        self.status = status
        self.mode = mode

        self.player1_uuid = player1_uuid
        self.player2_uuid = player2_uuid
        self.player1_symbol = player1_symbol
        self.player2_symbol = player2_symbol
        self.current_player_uuid = current_player_uuid

        self.winner_uuid = winner_uuid

        if board is None:
            self.board = Board()
        else:
            self.board = board

        self.created_at = created_at if created_at else datetime.utcnow()

    def is_waiting(self) -> bool:
        return self.status == GameStatus.WAITING and self.player2_uuid is None

    def is_in_progress(self) -> bool:
        return self.status == GameStatus.IN_PROGRESS

    def is_finished(self) -> bool:
        return self.status in [GameStatus.DRAW, GameStatus.WIN]

    def get_winner_uuid(self) -> str:
        if self.status != GameStatus.WIN:
            return None

        winner_symbol = self.board.get_winner()
        if winner_symbol == self.player1_symbol:
            return self.player1_uuid
        elif winner_symbol == self.player2_symbol:
            return self.player2_uuid
        return None

    def is_players_turn(self, player_uuid: str) -> bool:
        return self.current_player_uuid == player_uuid

    def switch_turn(self):
        if self.current_player_uuid == self.player1_uuid:
            self.current_player_uuid = self.player2_uuid
        else:
            self.current_player_uuid = self.player1_uuid