from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CreateGameRequest(BaseModel):
    mode: str = "pve"

class GameResponse(BaseModel):
    uuid: str
    mode: str
    status: str
    message: Optional[str] = None

class JoinGameResponse(BaseModel):
    uuid: str
    status: str
    message: str

class MoveRequest(BaseModel):
    field: List[List[int]]

class HistoryGameResponse(BaseModel):
    uuid: str
    mode: str
    status: str
    created_at: Optional[str] = None
    player1_uuid: Optional[str] = None
    player2_uuid: Optional[str] = None

class LeaderboardPlayer(BaseModel):
    login: str
    wins: int
    losses_draws: int
    win_ratio: float