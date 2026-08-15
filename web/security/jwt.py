import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Request, Depends
from sqlalchemy.orm import Session
from datasource.model.user_model import UserModel
from web.security.auth import get_db  # Импортируем готовую зависимость get_db

# Секретный ключ для подписи токенов (в реальном проекте хранится в .env)
SECRET_KEY = "your-super-secret-key-change-it-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # Токен живет 24 часа


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user_from_cookie(
        request: Request,
        db: Session = Depends(get_db)  # <-- ИСПРАВЛЕНИЕ ЗДЕСЬ: используем Depends и тип Session
) -> UserModel:
    """Получаем пользователя из JWT токена в cookie"""
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_uuid: str = payload.get("uuid")
        if user_uuid is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(UserModel).filter(UserModel.uuid == user_uuid).first()

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user