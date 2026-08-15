from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Берем URL из переменных окружения, если нет — используем значение по умолчанию
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres:1234@localhost:5432/tictactoe_db'
)

# Создаем движок SQLAlchemy (echo=False убирает спам SQL-запросами в консоль)
engine = create_engine(DATABASE_URL, echo=False)

# Базовый класс для моделей
Base = declarative_base()

# Фабрика сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Правильный паттерн FastAPI для получения сессии БД с гарантированным закрытием"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()