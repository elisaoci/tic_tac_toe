from sqlalchemy import Column, String, Integer, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datasource.database import Base
from domain.model.game_status import GameStatus


class GameModel(Base):
    """Модель игры в базе данных"""
    __tablename__ = 'games'

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_uuid = Column(UUID(as_uuid=True), nullable=False)  # UUID создателя игры

    # Новые поля для мультиплеера
    status = Column(SQLEnum(GameStatus), nullable=False, default=GameStatus.WAITING)
    mode = Column(String(10), nullable=False, default='pve')  # 'pve' или 'pvp'

    # Игроки
    player1_uuid = Column(UUID(as_uuid=True), nullable=True)
    player2_uuid = Column(UUID(as_uuid=True), nullable=True)
    player1_symbol = Column(Integer, nullable=True, default=1)  # 1 = X
    player2_symbol = Column(Integer, nullable=True, default=2)  # 2 = O
    current_player_uuid = Column(UUID(as_uuid=True), nullable=True)

    # Игровое поле
    field = Column(JSON, nullable=False, default=[[0, 0, 0], [0, 0, 0], [0, 0, 0]])
    current_player = Column(Integer, nullable=False, default=1)