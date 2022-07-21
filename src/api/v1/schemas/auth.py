from pydantic import BaseModel, Field, EmailStr


# Schema for registration
class UserSchema(BaseModel):
    username: str = Field(default=None)
    email: EmailStr = Field(default=None)
    password: str = Field(default=None)
    access_token: str = Field(default=None)
    refresh_token: str = Field(default=None)

    class Config:
        schema_extra = {
            "user_demo": {
                "username": "User1",
                "email": "example@test.com",
                "password": "1234"
            }
        }


# Schema for registration and login
class UserLoginSchema(BaseModel):
    username: str = Field(default=None)
    password: str = Field(default=None)

    class Config:
        schema_extra = {
            "user_demo": {
                "username": "mat",
                "password": "1234"
            }
        }
