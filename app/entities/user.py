from sqlmodel import Field

from app.core.user.enums import UserRole, UserStatus
from app.entities.base import TableBase, enum_field_info


class Tenant(TableBase, table=True):
    name: str = Field(max_length=255)
    email_domain: str = Field(max_length=255)
    is_active: bool = True
    is_setup: bool = False


class User(TableBase, table=True):
    tenant_id: int
    name: str = Field(max_length=255)
    email: str = Field(unique=True, max_length=255)

    full_name: str | None = Field(default=None, max_length=255)
    avatar: str | None = Field(default=None, max_length=255)

    hashed_password: str = Field(max_length=255)
    role: UserRole = enum_field_info(UserRole)
    status: UserStatus = enum_field_info(UserStatus, UserStatus.WaitActive)

    @property
    def is_superuser(self) -> bool:
        return self.role == UserRole.Owner or self.role == UserRole.Admin

    @property
    def is_active(self) -> bool:
        return self.status == UserStatus.Active

    @property
    def email_domain(self) -> str:
        return self.email.split("@", 2)[1]
