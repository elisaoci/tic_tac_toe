from sqlalchemy import Column, String, Integer, Enum as SQLEnum, JSON, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datasource.database import Base
from domain.model.game_status import GameStatus


class GameModel(Base):
    """Модель игры в базе данных"""
    __tablename__ = 'games'

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_uuid = Column(UUID(as_uuid=True), nullable=False)

    # ИСПРАВЛЕНИЕ: values_callable говорит SQLAlchemy использовать lowercase значения из Enum
    status = Column(
        SQLEnum(GameStatus, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=GameStatus.WAITING.value
    )
    mode = Column(String(10), nullable=False, default='pve')

    player1_uuid = Column(UUID(as_uuid=True), nullable=True)
    player2_uuid = Column(UUID(as_uuid=True), nullable=True)
    player1_symbol = Column(Integer, nullable=True, default=1)
    player2_symbol = Column(Integer, nullable=True, default=2)
    current_player_uuid = Column(UUID(as_uuid=True), nullable=True)

    field = Column(JSON, nullable=False, default=[[0, 0, 0], [0, 0, 0], [0, 0, 0]])
    current_player = Column(Integer, nullable=False, default=1)

    # Дата создания игры (время берется из PostgreSQL)
    created_at = Column(DateTime, nullable=False, server_default=func.now())