from urllib.request import Request

import redis
import uvicorn
from fastapi import FastAPI, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.api.v1.resources import posts
from src.core import config
from src.db import cache, redis_cache

from src.api.v1.schemas.auth import UserSchema
from src.api.v1.resources.jwt_handler import signJWT


app = FastAPI(
    # Конфигурируем название проекта. Оно будет отображаться в документации
    title=config.PROJECT_NAME,
    version=config.VERSION,
    # Адрес документации в красивом интерфейсе
    docs_url="/api/openapi",
    redoc_url="/api/redoc",
    # Адрес документации в формате OpenAPI
    openapi_url="/api/openapi.json",
)

# фейковая база данных зарегистрированных пользователей
users = []

@app.get("/")
def root():
    return {"service": config.PROJECT_NAME, "version": config.VERSION}


@app.on_event("startup")
def startup():
    """Подключаемся к базам при старте сервера"""
    cache.cache = redis_cache.CacheRedis(
        cache_instance=redis.Redis(
            host=config.REDIS_HOST, port=config.REDIS_PORT, max_connections=10
        )
    )


@app.on_event("shutdown")
def shutdown():
    """Отключаемся от баз при выключении сервера"""
    cache.cache.close()


# Подключаем роутеры к серверу
app.include_router(router=posts.router, prefix="/api/v1/posts")


# регистрация пользователя
@app.post("/api/v1/signup", tags=["user"], status_code=201)
def user_signup(user: UserSchema = Body(default=None)):
    users.append(user)
    return signJWT(user)


# проверка на наличие такого пользователя в БД
def get_user(data: UserSchema):
    for user in users:
        if user.username == data.username and user.password == data.password:
            return user
    return None


@app.post("/api/v1/login", tags=["user"])
def user_signup(user: UserSchema = Body(default=None)):
    persisted_user = get_user(user)
    if persisted_user is not None:
        # пользователь найден, возвращаю сохранённые данные + его access_token
        return persisted_user
    else:
        return {
            "error": "Логин или пароль не правильные"
        }


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def fake_decode_token(token):
    for user in users:
        if user.refresh_token == token:
            return user
    return None


@app.get("/api/v1/users/me")
async def read_users_me(current_user: UserSchema = Depends(get_current_user)):
    return current_user


if __name__ == "__main__":
    # Приложение может запускаться командой
    # `uvicorn main:app --host 0.0.0.0 --port 8000`
    # но чтобы не терять возможность использовать дебагер,
    # запустим uvicorn сервер через python
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
    )
