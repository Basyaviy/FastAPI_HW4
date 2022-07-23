from datetime import datetime
import uuid

from fastapi_jwt_auth import AuthJWT

from src.api.v1.resources.jwt_bearer import JWTBearer
from src.api.v1.resources.jwt_handler import generate_access_token, generate_refresh_token, get_uuid_from_token
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
    # на данном этапе токен не генерируется
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


def find_user_in_DB(uuid):
    for persisted_user in users:
        if persisted_user.uuid == uuid:
            return persisted_user


def generate_response_with_tokens(persisted_user: UserLoginSchema):
    access_token = generate_access_token(persisted_user)
    refresh_token = generate_refresh_token(persisted_user)
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


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post('/refresh', tags=["user"])
async def read_items(token: str = Depends(oauth2_scheme)):
    # декодировать токен и получить uuid пользователя
    uuid = get_uuid_from_token(token)
    persisted_user = find_user_in_DB(uuid)
    # обновить expiry датой для refresh_token
    refresh_token = generate_refresh_token(persisted_user)
    # обновить expiry датой для access_token
    access_token = generate_access_token(persisted_user)
    # вернуть новый токен
    return {"refresh_token": refresh_token, "access_token": access_token}


@router.get('/users/me', dependencies=[Depends(JWTBearer())], tags=["user"])
def about_me(token: str = Depends(oauth2_scheme)):
    # декодировать токен и получить uuid пользователя
    uuid = get_uuid_from_token(token)
    persisted_user = find_user_in_DB(uuid)
    if persisted_user is not None:
        # пользователь найден, формирую payload для access_token и refresh_token,
        # подписываю их и возвращаю пользователю
        return persisted_user


@router.patch('/users/me', dependencies=[Depends(JWTBearer())], tags=["user"])
def about_me(user: UserLoginSchema = Body(default=None), token: str = Depends(oauth2_scheme)):
    # декодировать токен и получить uuid пользователя
    uuid = get_uuid_from_token(token)
    persisted_user = find_user_in_DB(uuid)
    # Изменить данные на те что пришли в теле запроса
    persisted_user.username = user.username
    persisted_user.email = user.email
    # переподписать токены
    access_token = generate_access_token(persisted_user)

    if persisted_user is not None:
        # пользователь найден, формирую payload для access_token и refresh_token,
        # подписываю их и возвращаю пользователю
        return persisted_user