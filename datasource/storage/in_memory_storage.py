import threading
from typing import Dict
from uuid import UUID

class InMemoryStorage:
    _instance = None
    _lock = threading.RLock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._games: Dict[UUID, object] = {}
        return cls._instance

    def set(self, game_id: UUID, game_data: object):
        with self._lock:
            self._games[game_id] = game_data

    def get(self, game_id: UUID):
        with self._lock:
            return self._games.get(game_id)

    def delete(self, game_id: UUID):
        with self._lock:
            self._games.pop(game_id, None)