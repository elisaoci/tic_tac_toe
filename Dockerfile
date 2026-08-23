FROM python:3.11-slim

# Устанавливаем рабочую папку внутри контейнера
WORKDIR /app

# 1. Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. МАГИЯ ЗДЕСЬ:
# 'src/' со слэшем на конце означает "скопировать ВСЁ СОДЕРЖИМОЕ папки src"
# '.' означает "в текущую рабочую папку (/app)"
# В итоге в /app появятся app.py, web/, di/, domain/ и т.д.
COPY src/ .

# 3. Запускаем приложение. Так как app.py теперь лежит прямо в /app, пишем просто app:app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]