from domain.model.board import Board

def minimax(board: Board, depth: int = 0, is_maximizing: bool = True) -> int:
    winner = board.get_winner()
    if winner == Board.X:
        return -10 + depth
    if winner == Board.O:
        return 10 - depth
    if board.is_fill():
        return 0

    if is_maximizing:
        best_score = -999
        for row, col in board.get_free_moves():
            board.make_move(row, col)
            score = minimax(board, depth + 1, False)
            board.field[row][col] = Board.EMPTY
            board.current_player = Board.O
            best_score = max(best_score, score)
        return best_score
    else:
        best_score = 999
        for row, col in board.get_free_moves():
            board.make_move(row, col)
            score = minimax(board, depth + 1, True)
            board.field[row][col] = Board.EMPTY
            board.current_player = Board.X
            best_score = min(best_score, score)
        return best_score

def get_best_move(board: Board) -> tuple[int, int]:
    best_score = -999
    best_move = None
    for row, col in board.get_free_moves():
        board.make_move(row, col)
        score = minimax(board, 0, False)
        board.field[row][col] = Board.EMPTY
        board.current_player = Board.O
        if score > best_score:
            best_score = score
            best_move = (row, col)
    return best_move