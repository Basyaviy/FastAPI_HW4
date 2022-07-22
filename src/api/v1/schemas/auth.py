from datetime import datetime

from pydantic import BaseModel, Field, EmailStr
from fastapi import APIRouter
from typing import List, Optional

router = APIRouter()


class UserSchema(BaseModel):
    username: str = Field(default=None)
    roles: List[str] = Field(default=None)
    created_at: int = Field(default=None)
    is_superuser: bool = Field(default=False)
    uuid: str = Field(default=None)
    is_totp_enabled: bool = Field(default=False)
    is_active: bool = Field(default=True)
    email: EmailStr = Field(default=None)
    password: str = Field(default=None)
    # access_token: str = Field(default=None)
    # refresh_token: str = Field(default=None)

    class Config:
        schema_extra = {
            "user_demo": {
                "username": "User1",
                "email": "example@test.com",
                "password": "1234",
                "roles": "[]",
                "created_at": "2022-07-14T16 15:32",
                "is_superuser": "False",
                "uuid": "7a14-4g231-12sd122",
                "is_totp_enabled": "False",
                "is_active": "True",
                "access_token": "23j9048gfu30fu4309fu0439jf0394fsdc2fc23233",
                "refresh_token": "1df32908d239j8ndc2938d2n3923n892ncd23ncd0"
            }
        }


# Cхема для регистрации, то что должен получить сервер от клиента
class UserSignupSchema(BaseModel):
    username: str = Field(default=None)
    password: str = Field(default=None)
    email: str = Field(default=None)

    class Config:
        schema_extra = {
            "user_demo": {
                "username": "mat",
                "email": "mat@test.com",
                "password": "1234"
            }
        }


# Cхема для логина, то что должен получить сервер от клиента
class UserLoginSchema(BaseModel):
    username: str = Field(default=None)
    password: str = Field(default=None)
    email: str = Field(default=None)

    class Config:
        schema_extra = {
            "user_demo": {
                "username": "mat",
                "email": "mat@test.com",
                "password": "1234"
            }
        }
