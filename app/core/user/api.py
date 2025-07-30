from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from app.core.user.enums import PermissionResourceType, UserRole, UserStatus
from app.entities.user import User


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=4, max_length=40)
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
    created_at: datetime
    updated_at: datetime

    tenant_id: int
    name: str
    email: str

    full_name: str | None
    avatar: str | None

    role: UserRole
    status: UserStatus

    @staticmethod
    def create(entity: User) -> "UserPublic":
        return UserPublic(**entity.model_dump())


class UserUpdatePassword(BaseModel):

    current_password: str = Field(min_length=4, max_length=40)
    new_password: str = Field(min_length=4, max_length=40)


class AccessTokenPublic(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResetPassword(BaseModel):
    token: str
    new_password: str = Field(min_length=4, max_length=40)


class PermissionPublic(BaseModel):
    user_identify: str
    resource_type: PermissionResourceType
    resource_id: int
    role: UserRole


class PermissionRevoke(BaseModel):
    user_identify: str
    resource_type: PermissionResourceType
    resource_id: int


class PermissionGrant(PermissionRevoke):
    role: UserRole
