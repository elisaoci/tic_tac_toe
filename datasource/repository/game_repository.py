from typing import List, Optional
from sqlalchemy.orm import Session
from datasource.model.game_model import GameModel
from datasource.mapper.game_mapper import to_model, to_domain
from domain.model.game import Game
from domain.model.game_status import GameStatus


class SQLAlchemyGameRepository:
    """Репозиторий для работы с играми в БД"""

    def __init__(self, session: Session):
        self.session = session

    def save(self, game: Game) -> Game:
        """Сохранить или обновить игру"""
        model = to_model(game)
        self.session.merge(model)
        self.session.commit()
        return game

    def get(self, game_uuid: str) -> Optional[Game]:
        """Получить игру по UUID"""
        model = self.session.query(GameModel).filter(GameModel.uuid == game_uuid).first()
        if model:
            return to_domain(model)
        return None

    def get_all(self) -> List[Game]:
        """Получить все игры"""
        models = self.session.query(GameModel).all()
        return [to_domain(model) for model in models]

    def get_waiting_games(self) -> List[Game]:
        """Получить игры в статусе WAITING (для лобби PvP)"""
        models = self.session.query(GameModel).filter(
            GameModel.status == GameStatus.WAITING
        ).all()
        return [to_domain(model) for model in models]

    def delete(self, game_uuid: str) -> bool:
        """Удалить игру"""
        model = self.session.query(GameModel).filter(GameModel.uuid == game_uuid).first()
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False