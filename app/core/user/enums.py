from enum import StrEnum


class UserRole(StrEnum):
    Owner = "owner"
    Admin = "admin"
    Normal = "normal"
    Guest = "guest"


class UserStatus(StrEnum):
    WaitActive = "wait_active"
    Active = "active"
    Inactive = "inactive"
