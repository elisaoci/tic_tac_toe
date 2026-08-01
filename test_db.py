from di.database import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ Подключение к базе данных успешно!")
        print("Результат:", result.fetchone())
except Exception as e:
    print("❌ Ошибка подключения:", e)