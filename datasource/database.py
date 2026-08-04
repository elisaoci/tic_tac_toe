from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os

# Подключение к базе данных
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres:1234@localhost:5432/tictactoe_db'
)

# Создаем движок SQLAlchemy
engine = create_engine(DATABASE_URL, echo=False)

# Базовый класс для моделей
Base = declarative_base()

# Фабрика сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session():
    """Получить сессию базы данных"""
    return SessionLocal()