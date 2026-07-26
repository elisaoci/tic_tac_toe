import uuid
from .board import Board

class Game:
    def __init__(self, board: Board = None):
        self.uuid = str(uuid.uuid4())
        self.board = board or Board()