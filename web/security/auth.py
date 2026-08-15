from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPAuthorizationCredentials, HTTPBasicCredentials
from di.database import SessionLocal
from datasource.model.user_model import UserModel
from werkzeug.security import check_password_hash
import base64

security = HTTPBasic()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
        credentials: HTTPBasicCredentials = Depends(security),
        db: SessionLocal = Depends(get_db)
) -> UserModel:
    login = credentials.username
    password = credentials.password

    user = db.query(UserModel).filter(UserModel.login == login).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
            headers={"WWW-Authenticate": "Basic"},
        )

    if not check_password_hash(user.hashed_password, password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный пароль",
            headers={"WWW-Authenticate": "Basic"},
        )

    return user