# класс отвечает за подписывание, декодирование
# и получение токенов

import time
import jwt
# для работы с файлом настроек .env
from decouple import config

from src.api.v1.schemas.auth import UserSchema

JWT_SECRET = config("secret")
JWT_ALGORITHM = config("algorithm")


# returns generated Tokens (JWT)
def token_response(token: str):
    return token


# Sing the JWT payload
def signJWT(user: UserSchema):
    payload = {
        "username": user.username,
        "password": user.password,
        "expiry": time.time() + 600,
        "roles": [],
        "email": user.email,
    }
    # сохраняю токен в фейковую БД
    user.access_token = get_new_token(payload)
    user.refresh_token = get_new_token(payload)
    return user


def generate_payload(user):
    payload = {
        "username": user["username"],
        "password": user["password"],
        "expiry": time.time() + 600,
        "roles": [],
        "email": user["email"],
    }
    return payload


def get_new_token(user):
    return jwt.encode(generate_payload(user), JWT_SECRET, algorithm=JWT_ALGORITHM)


# base64 binary data
def decodeJWT(token: str):
    try:
        decode_token = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)
        if decode_token['expiry'] >= time.time():
            return decode_token
        return None
    except:
        return {
            "error": "Error in function decodeJWT"
        }
