from di.database import engine, Base
from datasource.model.user_model import UserModel  # Импортируем все модели
from datasource.model.game_model import GameModel

# Создаём все таблицы
Base.metadata.create_all(bind=engine)

print("✅ Таблицы созданы!")