from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional, List
from sqlalchemy.orm import Session

from domain.model.game import Game
from datasource.model.game_model import GameModel
from datasource.mapper.game_mapper import to_model, to_domain

class GameRepository(ABC):
    @abstractmethod
    def save(self, game: Game) -> None: ...

    @abstractmethod
    def get(self, game_id: str) -> Game | None: ...

    @abstractmethod
    def get_all(self) -> List[Game]: ...

class SQLAlchemyGameRepository(GameRepository):
    def __init__(self, session: Session):  # ← Принимает сессию извне
        self.session = session

    def save(self, game: Game) -> None:
        model = to_model(game)
        self.session.merge(model)
        self.session.commit()

    def get(self, game_id: str) -> Game | None:
        model = self.session.query(GameModel).filter_by(uuid=game_id).first()
        return to_domain(model) if model else None

    def get_all(self) -> List[Game]:
        model_list = self.session.query(GameModel).all()
        return [to_domain(model) for model in model_list]