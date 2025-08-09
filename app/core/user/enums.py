from enum import StrEnum
from typing import Self


class UserRole(StrEnum):
    Owner = "owner"
    Admin = "admin"
    Write = "write"
    Read = "read"

    def __init__(self, _):
        self.level: int = len(self.__class__.__members__)

    def implies(self, other: Self) -> bool:
        return self.level <= other.level

    @classmethod
    def super_roles(cls) -> list[Self]:
        return [cls.Owner, cls.Admin]


class UserStatus(StrEnum):
    WaitActive = "wait_active"
    Active = "active"
    Inactive = "inactive"


class PermissionResourceType(StrEnum):
    Workspace = "workspace"
    Knowledge = "knowledge"
    Workflow = "workflow"
