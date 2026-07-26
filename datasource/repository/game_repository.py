from abc import ABC, abstractmethod
from uuid import UUID
from domain.model.game import Game
from datasource.storage.in_memory_storage import InMemoryStorage
from datasource.mapper.game_mapper import to_datasource, to_domain

class GameRepository(ABC):
    @abstractmethod
    def save(self, game: Game) -> None: ...

    @abstractmethod
    def get(self, game_id: UUID) -> Game | None: ...

class InMemoryGameRepository(GameRepository):
    def __init__(self):
        self.storage = InMemoryStorage()

    def save(self, game: Game) -> None:
        ds = to_datasource(game)
        self.storage.set(ds.uuid, ds)

    def get(self, game_id: UUID) -> Game | None:
        ds = self.storage.get(game_id)
        return to_domain(ds) if ds else None