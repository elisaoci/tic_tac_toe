from typing import List, Optional

class Board:
    EMPTY = 0
    X = 1
    O = 2

    def __init__(self):
        self.field: List[List[int]] = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]
        self.current_player = self.X

    def make_move(self, row: int, col: int) -> bool:
        if self.field[row][col] != self.EMPTY:
            return False
        self.field[row][col] = self.current_player
        self.current_player = self.O if self.current_player == self.X else self.X
        return True

    def is_fill(self) -> bool:
        return all(cell != self.EMPTY for row in self.field for cell in row)

    def get_winner(self) -> Optional[int]:
        lines = self.field + list(map(list, zip(*self.field))) + [[self.field[i][i] for i in range(3)]] + [[self.field[i][2-i] for i in range(3)]]

        for line in lines:
            if line[0] == line[1] == line[2] != self.EMPTY:
                return line[0]
        return None

    def copy(self) -> 'Board':
        new_board = Board()
        new_board.field = [row[:] for row in self.field]
        new_board.current_player = self.current_player
        return new_board

    def get_free_moves(self):
        return [(r, c) for r in range(3) for c in range(3) if self.field[r][c] == self.EMPTY]