from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datasource.model.game_model import GameModel
from datasource.mapper.game_mapper import to_model, to_domain
from domain.model.game import Game
from domain.model.game_status import GameStatus
from datetime import datetime, timedelta

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
        """Получить игры в статусе WAITING"""
        cutoff_time = datetime.utcnow() - timedelta(hours=24)

        models = self.session.query(GameModel).filter(
            GameModel.status == GameStatus.WAITING,
            GameModel.created_at >= cutoff_time
        ).order_by(GameModel.created_at.desc()).all()

        return [to_domain(model) for model in models]

    def get_finished_games_by_user(self, user_uuid: str) -> List[Game]:
        """Получить все завершенные игры пользователя"""
        # Игра завершена, если:
        # 1. Статус WIN и пользователь выиграл (его UUID совпадает с winner_uuid)
        # 2. Статус DRAW (ничья)

        # Сначала получаем все игры пользователя
        models = self.session.query(GameModel).filter(
            or_(
                GameModel.player1_uuid == user_uuid,
                GameModel.player2_uuid == user_uuid
            )
        ).all()

        # Фильтруем только завершенные
        finished_games = []
        for model in models:
            game = to_domain(model)
            # Проверяем, завершена ли игра
            if game.status == GameStatus.DRAW:
                finished_games.append(game)
            elif game.status == GameStatus.WIN:
                # Проверяем, выиграл ли именно этот пользователь
                winner_uuid = game.get_winner_uuid()
                if winner_uuid == user_uuid:
                    finished_games.append(game)

        return finished_games

    def delete(self, game_uuid: str) -> bool:
        """Удалить игру"""
        model = self.session.query(GameModel).filter(GameModel.uuid == game_uuid).first()
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False