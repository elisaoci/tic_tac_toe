from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os


DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres:1234@localhost:5432/tictactoe_db'
)

engine = create_engine(DATABASE_URL, echo=False)

Base = declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()