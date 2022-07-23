# класс отвечает за подписывание, декодирование
# и получение токенов

import time
from math import floor

import jwt
from src.core import config

from src.api.v1.schemas.auth import UserSchema

JWT_SECRET = config.JWT_SECRET_KEY
JWT_ALGORITHM = config.JWT_ALGORITHM


# returns generated Tokens (JWT)
def token_response(token: str):
    return token


# Эти два метода для формирования payload которые будут добавлены в JWT токены
# отличаются количеством передаваемых атрибутов и сроком протухания
def generate_access_token(user: UserSchema):
    payload = {
        "username": user.username,
        "roles": user.roles,
        "created_at": user.created_at,
        "is_superuser": user.is_superuser,
        "uuid": user.uuid,
        "is_totp_enabled": user.is_totp_enabled,
        "is_active": user.is_active,
        "email": user.email,
        "expiry": floor(time.time()) + 300,
    }
    return signJWT(payload)


def generate_refresh_token(user: UserSchema):
    payload = {
        "uuid": user.uuid,
        "expiry": floor(time.time()) + 600,
    }
    return signJWT(payload)


# Sign the JWT payload
def signJWT(payload):
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


# расшифровать JWT токен из base64 чтобы проверить дату протухания
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


# Используется для обновления токена
# Декодирует полученный токен и достаёт uuid пользователя чтобы поискать такого в БД
def get_uuid_from_token(token: str):
    try:
        decode_token = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)
        return decode_token['uuid']
    except:
        return {
            "error": "Error in function get_uuid_from_token"
        }