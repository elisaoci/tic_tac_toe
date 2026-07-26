from abc import ABC, abstractmethod
from domain.model.game import Game

class GameService(ABC):
    @abstractmethod
    def get_computer_move(self, game: Game) -> Game:
        """Возвращает игру после хода компьютера (Минимакс)"""

    @abstractmethod
    def check_player_move(self, old_game: Game, new_game: Game) -> bool:
        """Проверяет, что игрок сделал ровно один корректный ход и не менял старые клетки"""

    @abstractmethod
    def is_game_over(self, game: Game) -> bool:
        """Проверка на окончание игры (победа или ничья)"""