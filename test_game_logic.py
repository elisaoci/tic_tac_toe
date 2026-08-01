from domain.model.board import Board
from domain.model.game import Game


def test_board_logic():
    print("=== Тест 1: Логика доски (Board) ===")

    # 1. Тест победы
    board = Board()
    board.field = [[1, 1, 1], [0, 2, 0], [2, 0, 2]]  # Игрок выиграл по горизонтали
    print(f" Поле: {board.field}")
    print(f"   Победитель: {board.get_winner()} (Ожидалось: 1)")
    print(f"   Поле заполнено: {board.is_fill()} (Ожидалось: False)")

    # 2. Тест ничьей
    board2 = Board()
    board2.field = [[1, 2, 1], [1, 2, 2], [2, 1, 1]]  # Ничья
    print(f"\n🔹 Поле: {board2.field}")
    print(f"   Победитель: {board2.get_winner()} (Ожидалось: None)")
    print(f"   Поле заполнено: {board2.is_fill()} (Ожидалось: True)")


def test_controller_flow():
    print("\n=== Тест 2: Симуляция последнего хода (Ничья) ===")

    # Создаем игру
    game = Game()

    # Предпоследнее состояние (осталась одна пустая клетка в углу [2][2])
    game.board.field = [[1, 2, 1], [1, 2, 2], [2, 1, 0]]
    print(f"🔹 До хода игрока: {game.board.field}")

    # --- Симуляция того, что делает контроллер ---

    # 1. Игрок делает ход в последнюю клетку
    game.board.field[2][2] = 1
    # 2. Контроллер передает ход компьютеру
    game.board.current_player = 2

    print(f"🔹 После хода игрока: {game.board.field}")

    # 3. Проверяем состояние
    winner = game.board.get_winner()
    is_fill = game.board.is_fill()

    print(f"   Победитель: {winner}")
    print(f"   Поле заполнено: {is_fill}")

    # 4. Решение: должен ли ходить компьютер?
    if winner or is_fill:
        print("✅ Вердикт: Игра закончена! Компьютер НЕ должен делать ход и сохранять свой вариант.")
    else:
        print("❌ Вердикт: Игра не закончена. Компьютер должен сделать ход.")


if __name__ == "__main__":
    test_board_logic()
    test_controller_flow()