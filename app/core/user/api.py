from pydantic import BaseModel, Field, EmailStr

from app.config import settings
from app.core.user.enums import UserRole, UserStatus


class UserCreate(BaseModel):
    email: EmailStr
    role: UserRole

    @property
    def name(self) -> str:
        return str(self.email).split("@", 2)[0]

    @property
    def email_domain(self) -> str:
        return str(self.email).split("@", 2)[1]


class UserUpdateMe(BaseModel):
    full_name: str | None = Field(default=None, max_length=255)
    avatar: str | None = Field(default=None, max_length=255)


class UserUpdate(UserUpdateMe):
    email: str


class UserPublic(BaseModel):
    tenant_id: int
    name: str
    email: str

    full_name: str | None
    avatar: str | None

    role: UserRole
    status: UserStatus


class UserUpdatePassword(BaseModel):

    current_password: str = Field(min_length=4, max_length=40)
    new_password: str = Field(min_length=4, max_length=40)


class AccessTokenPublic(BaseModel):
    access_token: str
    token_type: str = settings.ACCESS_TOKEN_TYPE


class UserResetPassword(BaseModel):
    token: str
    new_password: str = Field(min_length=4, max_length=40)
