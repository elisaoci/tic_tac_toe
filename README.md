# Крестики-нолики (Tic-Tac-Toe)

Многопользовательская веб-игра с полноценной серверной логикой, системой безопасной авторизации, рейтинговой таблицей и режимом игры против непобедимого ИИ.

## Механика и возможности

- **Авторизация и безопасность**: Регистрация и вход с использованием JWT-токенов, сохраняемых в HttpOnly cookies (защита от XSS).
- **Два режима игры**:
· PvP: Игра против другого реального игрока через систему лобби.
· PvE: Игра против компьютера, использующего алгоритм Minimax для выбора оптимального хода.
- **Умное лобби**: Автоматическая фильтрация игр (пользователь не видит игры, которые создал сам, чтобы избежать игры "против себя").
- **История игр**: Детальный журнал всех завершенных партий с указанием результата (победа, поражение, ничья).
- **Таблица лидеров**: Динамический рейтинг игроков с расчетом коэффициента побед (win_ratio) на основе сложных SQL-агрегаций.
- **Защита от читерства**: Полная валидация ходов, очередности и состояния игры на стороне сервера.

## Технологии

- Backend: Python 3.10+, FastAPI, Uvicorn
- База данных: PostgreSQL, SQLAlchemy 2.0 (ORM)
- Валидация и схемы: Pydantic
- Безопасность: PyJWT, Werkzeug (хеширование паролей)
- Frontend: HTML5, CSS3, Vanilla JavaScript (Fetch API), Jinja2 (шаблонизатор)
- Инфраструктура: Docker, Docker Compose
- Архитектура: Clean Architecture / Layered Architecture, Паттерн Repository, Dependency Injection

## Быстрый запуск (через Docker)

1.  Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/tic_tac_toe.git
cd tic_tac_toe
```

2. Запустите приложение и базу данных одной командой:
```bash
docker compose up --build
```

3. Откройте браузер и перейдите по адресу: http://127.0.0.1:8000

## Локальный запуск 

1. Клонируйте репозиторий и перейдите в папку src:
```bash
git clone https://github.com/your-username/tic_tac_toe.git
cd tic_tac_toe/src
```

2. Создайте и активируйте виртуальное окружение:
```bash
python -m venv .venv
source .venv/bin/activate  # Для Windows: .venv\Scripts\activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл .env (скопируйте .env.example) и укажите свой DATABASE_URL.
  
5. Запустите приложение:
```bash
python app.py
```

6. Откройте браузер по адресу: http://127.0.0.1:8000

7. Документация API (Swagger UI) доступна по адресу: http://127.0.0.1:8000/docs
   
## Структура проекта
Проект разделен на логические слои для обеспечения слабосвязанности и тестируемости:
```text
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── README.md
├── docker-compose.yml
├── requirements.txt
└── src
    ├── __init__.py
    ├── app.py
    ├── datasource
    │   ├── __init__.py
    │   ├── mapper
    │   │   ├── __init__.py
    │   │   └── game_mapper.py
    │   ├── model
    │   │   ├── __init__.py
    │   │   ├── game_model.py
    │   │   └── user_model.py
    │   └── repository
    │       ├── __init__.py
    │       ├── game_repository.py
    │       └── user_repository.py
    ├── di
    │   ├── __init__.py
    │   ├── container.py
    │   └── database.py
    ├── domain
    │   ├── __init__.py
    │   ├── model
    │   │   ├── __init__.py
    │   │   ├── board.py
    │   │   ├── game.py
    │   │   └── game_status.py
    │   ├── repository
    │   │   ├── __init__.py
    │   │   └── user_repository_interface.py
    │   └── service
    │       ├── __init__.py
    │       ├── game_service.py
    │       ├── game_service_interface.py
    │       └── user_service.py
    ├── helpers
    │   ├── __init__.py
    │   └── minimax.py
    ├── static
    │   └── style.css
    ├── templates
    │   ├── create_game.html
    │   ├── game.html
    │   ├── history.html
    │   ├── leaderboard.html
    │   ├── lobby.html
    │   ├── login.html
    │   └── register.html
    └── web
        ├── __init__.py
        ├── routers
        │   ├── __init__.py
        │   ├── auth_router.py
        │   └── game_router.py
        ├── schemas
        │   ├── __init__.py
        │   ├── auth.py
        │   └── game.py
        └── security
            ├── __init__.py
            ├── auth.py
            └── jwt.py

```

## Выходные данные и интерфейс

- **Интерактивный веб-интерфейс**: Адаптивные страницы для лобби, игрового поля, истории и рейтинга.
- **RESTful API**: Полное покрытие всех действий эндпоинтами с кодами ответов HTTP (200, 201, 400, 401, 404).
- **Итоговая статистика**:
· Личная история матчей с цветовой индикацией результатов.
· Глобальная таблица лидеров с подсчетом общего числа побед, поражений/ничьих и `win_ratio`.
  
## Что демонстрирует этот проект

- **Архитектурные паттерны**: Строгое разделение ответственности (Domain, Datasource, Web), использование Dependency Injection и паттерна Repository.
- **Безопасность (Security)**: Правильная реализация stateless-аутентификации через JWT в HttpOnly cookies и корректное управление сессиями (логаут).
- **Работа с БД**: Использование сложных SQL-запросов (CTE, UNION ALL, агрегатные функции) для эффективного расчета статистики без перегрузки Python-кода.
- **Алгоритмическое мышление**: Реализация алгоритма Minimax для создания интеллектуального противника.
- **Надежность и DevOps**: Серверная валидация каждого действия, предотвращающая некорректные состояния игры (race conditions, читы на клиенте), а также полная контейнеризация проекта для воспроизводимого развертывания в любой среде.
