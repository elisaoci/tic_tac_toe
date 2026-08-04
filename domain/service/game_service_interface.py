from abc import ABC, abstractmethod
from domain.model.game import Game


class GameService(ABC):
    """Интерфейс сервиса игры"""

    @abstractmethod
    def create_game(self, player_uuid: str, mode: str = "pve") -> Game:
        """
        Создать новую игру.
        - Для pve: сразу добавляет компьютер как player2, статус IN_PROGRESS
        - Для pvp: создает игру в статусе WAITING
        """
        pass

    @abstractmethod
    def join_game(self, game_uuid: str, player_uuid: str) -> Game:
        """
        Присоединиться к существующей игре (только для PvP).
        Меняет статус на IN_PROGRESS.
        """
        pass

    @abstractmethod
    def make_move(self, game_uuid: str, player_uuid: str, field: list) -> Game:
        """
        Сделать ход игрока.
        - Для pve: после хода игрока делает ход компьютер
        - Для pvp: просто применяет ход и переключает очередь
        """
        pass

    @abstractmethod
    def get_game(self, game_uuid: str) -> Game:
        """Получить игру по UUID"""
        pass

    @abstractmethod
    def get_available_games(self) -> list:
        """Получить список игр в статусе WAITING (для лобби PvP)"""
        pass

    @abstractmethod
    def check_player_move(self, old_game: Game, new_field: list) -> bool:
        """Проверить, что ход игрока валиден (изменена только одна клетка)"""
        pass

    @abstractmethod
    def is_game_over(self, game: Game) -> bool:
        """Проверить, закончена ли игра"""
        pass