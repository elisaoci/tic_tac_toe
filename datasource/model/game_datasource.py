from dataclasses import dataclass
from uuid import UUID
from typing import List

@dataclass
class GameDatasource:
    uuid: UUID
    field: List[List[int]]
    current_player: int