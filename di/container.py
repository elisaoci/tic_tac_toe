from datasource.repository.game_repository import InMemoryGameRepository
from domain.service.game_service import GameServiceImpl

class Container:
    def __init__(self):
        self._repository = InMemoryGameRepository()
        self._game_service = GameServiceImpl(repository=self._repository)

    @property
    def game_service(self):
        return self._game_service

    @property
    def repository(self):
        return self._repository