import uuid
from domain.model.board import Board


class Game:
    def __init__(self, board: Board = None, user_uuid: str = None):
        self.uuid = str(uuid.uuid4())
        self.user_uuid = user_uuid

        if board is None:
            self.board = Board()
        else:
            self.board = board