# Файл: src/init_db.py
from di.database import Base, engine

# Пытаемся импортировать модели
try:
    from datasource.model.user_model import UserModel
    print("✅ UserModel импортирован успешно")
except ImportError as e:
    print(f"❌ Ошибка импорта UserModel: {e}")

try:
    from datasource.model.game_model import GameModel
    print("✅ GameModel импортирован успешно")
except ImportError as e:
    print(f"❌ Ошибка импорта GameModel: {e}")

print("\n🔄 Таблицы, которые SQLAlchemy видит ПЕРЕД созданием:")
for table_name in Base.metadata.tables.keys():
    print(f"  👉 {table_name}")

print("\n🔄 Запуск создания таблиц...")
Base.metadata.create_all(bind=engine)
print("✅ Готово!")