from enum import Enum


class GameStatus(Enum):
    WAITING = "waiting"           # Ожидание второго игрока
    IN_PROGRESS = "in_progress"   # Игра идет
    DRAW = "draw"                 # Ничья
    WIN = "win"                   # Кто-то победил