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


# Эти два метода для формирования payload которые будут добавлены в JWT токены
# отличаются количеством передаваемых атрибутов и сроком протухания
def get_access_token(user: UserSchema):
    payload = {
        "username": user.username,
        "roles": user.roles,
        "created_at": user.created_at,
        "is_superuser": user.is_superuser,
        "uuid": user.uuid,
        "is_totp_enabled": user.is_totp_enabled,
        "is_active": user.is_active,
        "email": user.email,
        "expiry": time.time() + 300,
    }
    return signJWT(payload)


def get_refresh_token(user: UserSchema):
    payload = {
        "uuid": user.uuid,
        "expiry": time.time() + 600,
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
