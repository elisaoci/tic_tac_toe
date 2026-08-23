from fastapi import APIRouter, Depends, HTTPException, Response, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from web.schemas.auth import RegisterRequest, RegisterResponse, LoginRequest
from web.security.auth import get_db
from web.security.jwt import create_access_token, get_current_user_from_cookie
from di.database import SessionLocal
from datasource.model.user_model import UserModel
from werkzeug.security import generate_password_hash, check_password_hash
import uuid as uuid_lib

router = APIRouter(prefix="/auth", tags=["Авторизация"])
templates = Jinja2Templates(directory="templates")


@router.post("/register", response_model=RegisterResponse, status_code=201)
def register(request: RegisterRequest, db: SessionLocal = Depends(get_db)):
    existing_user = db.query(UserModel).filter(UserModel.login == request.login).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    new_user = UserModel(
        uuid=str(uuid_lib.uuid4()),
        login=request.login,
        hashed_password=generate_password_hash(request.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return RegisterResponse(message="Пользователь зарегистрирован", uuid=str(new_user.uuid))


@router.post("/login")
def login(request: LoginRequest, response: Response, db: SessionLocal = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.login == request.login).first()
    if not user or not check_password_hash(user.hashed_password, request.password):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    token = create_access_token(data={"uuid": str(user.uuid), "sub": user.login})

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=86400,
        path="/"
    )

    return {"message": "Вход выполнен успешно", "uuid": str(user.uuid)}


@router.get("/logout")
def logout(response: Response):
    response.set_cookie(
        key="access_token",
        value="",
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=0,
        path="/"
    )
    return RedirectResponse(url="/?logout=1", status_code=303)

@router.get("/me")
def get_me(current_user: UserModel = Depends(get_current_user_from_cookie)):
    return {"uuid": str(current_user.uuid), "login": current_user.login}

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        request,
        name="login.html",
        context={}
    )


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(
        request,
        name="register.html",
        context={}
    )