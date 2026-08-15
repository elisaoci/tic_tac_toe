from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from web.routers.auth_router import router as auth_router
from web.routers.game_router import router as game_router
import uvicorn

from di.database import Base, engine
from datasource.model.user_model import UserModel
from datasource.model.game_model import GameModel

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Крестики-нолики API",
    description="Многопользовательская игра на FastAPI",
    version="2.0.0"
)

# Подключаем статические файлы (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Подключаем роутеры
app.include_router(auth_router)
app.include_router(game_router)


@app.exception_handler(401)
async def unauthorized_exception_handler(request: Request, exc: StarletteHTTPException):
    """При ошибке 401 перенаправляем на главную (для HTML) или возвращаем JSON (для API)"""
    accept_header = request.headers.get("accept", "")

    if "text/html" in accept_header:
        # Для браузера — редирект на главную
        return RedirectResponse(url="/", status_code=303)
    else:
        # Для API/Swagger — возвращаем JSON
        return JSONResponse(
            status_code=401,
            content={"detail": "Not authenticated"}
        )


@app.get("/", response_class=HTMLResponse)
def root(request: Request, logout: int = 0):
    # Проверяем валидность токена
    token = request.cookies.get("access_token")
    is_authenticated = False

    # Если logout=1, точно не авторизован
    if logout == 1:
        is_authenticated = False
    # Иначе проверяем токен
    elif token and token.strip():
        try:
            import jwt
            from web.security.jwt import SECRET_KEY, ALGORITHM
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            is_authenticated = True
        except jwt.PyJWTError:
            is_authenticated = False

    return f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
        <meta http-equiv="Pragma" content="no-cache">
        <meta http-equiv="Expires" content="0">
        <title>Крестики-нолики</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; text-align: center; }}
            h1 {{ color: #333; }}
            .menu {{ list-style: none; padding: 0; }}
            .menu li {{ margin: 15px 0; }}
            .menu a {{
                display: inline-block;
                padding: 12px 24px;
                background-color: #2196F3;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                font-size: 18px;
            }}
            .menu a:hover {{ background-color: #0b7dda; }}
            .secondary a {{ background-color: #757575; }}
            .secondary a:hover {{ background-color: #616161; }}
            .logout-message {{ color: green; margin-top: 20px; font-size: 18px; }}
        </style>
    </head>
    <body>
        <h1>🎮 Крестики-нолики (FastAPI)</h1>
        <p>✅ Сервер работает!</p>
        {'<p class="logout-message">Вы успешно вышли из системы</p>' if logout == 1 else ''}
        <ul class="menu" id="menu">
            <li><a href="/auth/login">🔐 Войти в систему</a></li>
            <li><a href="/games/lobby">👀 Посмотреть лобби (без входа)</a></li>
        </ul>
        <ul class="menu secondary">
            <li><a href="/docs"> Swagger UI (Документация API)</a></li>
        </ul>

        <script>
            // Принудительно удаляем cookie на клиенте
            document.cookie = "access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";

            // Если сервер сказал, что пользователь авторизован, показываем полное меню
            const isAuth = {"true" if is_authenticated else "false"};
            if (isAuth) {{
                document.getElementById('menu').innerHTML = `
                    <li><a href="/games/new"> Начать игру</a></li>
                    <li><a href="/games/lobby"> Лобби игр</a></li>
                    <li><a href="/history">📜 История игр</a></li>
                    <li><a href="/leaderboard_page">🏆 Таблица лидеров</a></li>
                    <li><a href="/auth/logout">🚪 Выйти</a></li>
                `;
            }}
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)