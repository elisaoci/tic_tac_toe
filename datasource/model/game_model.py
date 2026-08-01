from sqlalchemy import Column, String, Integer, JSON
from di.database import Base


class GameModel(Base):
    __tablename__ = "games"

    uuid = Column(String, primary_key=True)
    user_uuid = Column(String, nullable=False)
    field = Column(JSON)
    current_player = Column(Integer)