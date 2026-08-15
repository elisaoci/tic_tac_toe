from abc import ABC, abstractmethod
from domain.model.game import Game


class GameService(ABC):

    @abstractmethod
    def create_game(self, player_uuid: str, mode: str = "pve") -> Game:
        pass

    @abstractmethod
    def join_game(self, game_uuid: str, player_uuid: str) -> Game:
        pass

    @abstractmethod
    def make_move(self, game_uuid: str, player_uuid: str, field: list) -> Game:
        pass

    @abstractmethod
    def get_game(self, game_uuid: str) -> Game:
        pass

    @abstractmethod
    def get_available_games(self) -> list:
        pass

    @abstractmethod
    def check_player_move(self, old_game: Game, new_field: list) -> bool:
        pass

    @abstractmethod
    def is_game_over(self, game: Game) -> bool:
        pass