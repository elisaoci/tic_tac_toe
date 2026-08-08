from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datasource.model.game_model import GameModel
from datasource.mapper.game_mapper import to_model, to_domain
from domain.model.game import Game
from domain.model.game_status import GameStatus
from datetime import datetime, timedelta
from sqlalchemy import text

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

    def get_top_players(self, limit: int) -> list:
        """Получить топ-N игроков по соотношению побед (только PvP игры)"""
        query = text("""
            WITH user_stats AS (
                -- Статистика как Player 1
                SELECT 
                    player1_uuid as user_uuid,
                    SUM(CASE WHEN status = 'win' AND winner_uuid = player1_uuid THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN status = 'draw' OR (status = 'win' AND winner_uuid != player1_uuid) THEN 1 ELSE 0 END) as losses_draws
                FROM games
                WHERE player1_uuid IS NOT NULL 
                AND player1_uuid != '00000000-0000-0000-0000-000000000000'
                AND player2_uuid IS NOT NULL
                AND player2_uuid != '00000000-0000-0000-0000-000000000000'
                GROUP BY player1_uuid

                UNION ALL

                -- Статистика как Player 2
                SELECT 
                    player2_uuid as user_uuid,
                    SUM(CASE WHEN status = 'win' AND winner_uuid = player2_uuid THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN status = 'draw' OR (status = 'win' AND winner_uuid != player2_uuid) THEN 1 ELSE 0 END) as losses_draws
                FROM games
                WHERE player1_uuid IS NOT NULL 
                AND player1_uuid != '00000000-0000-0000-0000-000000000000'
                AND player2_uuid IS NOT NULL
                AND player2_uuid != '00000000-0000-0000-0000-000000000000'
                GROUP BY player2_uuid
            )
            SELECT 
                user_uuid,
                SUM(wins) as total_wins,
                SUM(losses_draws) as total_losses_draws,
                -- NULLIF защищает от ошибки "division by zero"
                SUM(wins)::float / NULLIF(SUM(losses_draws), 0) as win_ratio
            FROM user_stats
            GROUP BY user_uuid
            ORDER BY win_ratio DESC NULLS LAST
            LIMIT :limit
        """)

        result = self.session.execute(query, {"limit": limit}).fetchall()
        return [
            {
                "user_uuid": str(row.user_uuid),
                "total_wins": row.total_wins,
                "total_losses_draws": row.total_losses_draws,
                "win_ratio": float(row.win_ratio) if row.win_ratio else 0.0
            }
            for row in result
        ]