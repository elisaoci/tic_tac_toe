from dataclasses import dataclass
from typing import List

@dataclass
class GameRequest:
    uuid: str
    field: List[List[int]]