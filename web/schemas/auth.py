from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class RegisterRequest(BaseModel):
    login: str = Field(..., min_length=3, max_length=50, description="Логин пользователя")
    password: str = Field(..., min_length=6, description="Пароль (минимум 6 символов)")

class RegisterResponse(BaseModel):
    message: str
    uuid: str

class LoginRequest(BaseModel):
    login: str
    password: str

class LoginResponse(BaseModel):
    uuid: str
    login: str
    message: str

class UserResponse(BaseModel):
    uuid: str
    login: str
    created_at: Optional[datetime] = None