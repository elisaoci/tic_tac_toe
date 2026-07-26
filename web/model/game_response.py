from dataclasses import dataclass
from typing import List, Optional

@dataclass
class GameResponse:
    uuid: str
    field: List[List[int]]
    winner: Optional[int] = None
    is_over: bool = False