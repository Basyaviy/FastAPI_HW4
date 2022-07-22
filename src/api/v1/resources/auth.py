from datetime import datetime
import uuid

from fastapi_jwt_auth import AuthJWT

from src.api.v1.resources.jwt_handler import get_access_token, get_refresh_token
from src.api.v1.schemas.auth import UserSchema, UserLoginSchema, UserSignupSchema
from fastapi import Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter

router = APIRouter()

# Префикс для фейкового хеширования пароля
hash_prefix = "fakeencoded"

# Фейковая база данных зарегистрированных пользователей
users = []

# регистрация пользователя
@router.post("/signup", tags=["user"], status_code=201)
def user_signup(user: UserSignupSchema = Body(default=None)):
    response_user = create_user(user)

    # возвращаем пользователю данные об успешной регистрации
    # на данном этам токен не генерируется
    # return signJWT(user)
    result = {
        "msg" : "User created.",
        "user": response_user
    }

    return result


# Функция создания записи о пользователе данные полученные от пользователя.
def create_user(user: UserSignupSchema):
    # Предполагаем что такого пользователя в БД ещё нет
    # дополнение записей о пользователе
    persisted_user = UserSchema()
    persisted_user.username = user.username
    # TODO TypeError: Object of type datetime is not JSON serializable
    persisted_user.created_at = datetime.now().timestamp()
    persisted_user.email = user.email
    persisted_user.password = encode_password(user.password)
    persisted_user.uuid = uuid.uuid1().urn
    persisted_user.roles = []
    users.append(persisted_user)
    return persisted_user


# Хеширование пароля для хранения в БД.
# TODO сделать настоящее хеширование пароля
def encode_password(password: str):
    return hash_prefix + password


# Проверка полученного от пользователя пароля с захешированным паролем из БД.
def check_password(password: str, hashed_password: str):
    return encode_password(password) == hashed_password


# Проверяю на наличие такого пользователя в БД.
# Проверяю введённый пароль.
def get_user(user: UserSchema):
    for persisted_user in users:
        if persisted_user.username == user.username and check_password(user.password, persisted_user.password):
            return persisted_user
    return None


def generate_response_with_tokens(persisted_user: UserLoginSchema):
    access_token = get_access_token(persisted_user)
    refresh_token = get_refresh_token(persisted_user)
    result = {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }
    return result


@router.post("/login", tags=["user"])
def user_signup(user: UserLoginSchema = Body(default=None), Authorize: AuthJWT = Depends()):
    # Authorize.create_access_token()
    persisted_user = get_user(user)
    if persisted_user is not None:
        # пользователь найден, формирую payload для access_token и refresh_token,
        # подписываю их и возвращаю пользователю
        return generate_response_with_tokens(persisted_user)
    else:
        return {
            "error": "Логин или пароль не правильные"
        }


@router.post('/refresh', tags=["user"])
def refresh(Authorize: AuthJWT = Depends()):
    Authorize.jwt_refresh_token_required()
    current_user = Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(subject=current_user)
    return {"access_token": new_access_token}

# Example protected Endpoint
@router.get('/hello')
def refresh(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    return {"hello": "world"}