from datetime import timedelta
from typing import Literal, Self

from fastapi.params import Query
from pydantic_settings import BaseSettings
from pydantic import EmailStr, model_validator


class ApiSettings(BaseSettings):
    PROJECT_NAME: str
    API_PREFIX_STR: str = "/api/v1"

    SECRET_KEY: str
    SECRET_ALGORITHM: Literal["RS256", "HS256"] = "RS256"
    ACCESS_TOKEN_TYPE: str = "bearer"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10
    ACCESS_TOKEN_RESET_EXPIRE_HOURS: int = 24

    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: str | None = None

    DEFAULT_PAGE_SIZE: int = 20
    DEFAULT_MAX_PAGE_SIZE: int = 1000
    DEFAULT_MAX_PAGE_NO: int = 100000

    @property
    def token_expire_timedelta(self) -> timedelta:
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)

    @property
    def token_reset_expire_timedelta(self) -> timedelta:
        return timedelta(hours=self.ACCESS_TOKEN_RESET_EXPIRE_HOURS)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def emails_enabled(self) -> bool:
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)

    @property
    def page_no_query(self) -> Query:
        return Query(default=1, ge=1, le=self.DEFAULT_MAX_PAGE_NO)

    @property
    def page_size_query(self) -> Query:
        return Query(default=self.DEFAULT_PAGE_SIZE,
                     ge=1, le=self.DEFAULT_MAX_PAGE_SIZE)

    @model_validator(mode="after")
    def _set_default_emails_from(self) -> Self:
        if not self.EMAILS_FROM_NAME:
            self.EMAILS_FROM_NAME = self.PROJECT_NAME
        return self
