from typing import Literal

from pydantic import Field, PositiveFloat
from pydantic import (
    computed_field,
)
from pydantic_settings import BaseSettings


class CeleryConfig(BaseSettings):
    CELERY_BACKEND: Literal["database", "redis"] = Field(
        description="backend for task results",
        default="database",
    )

    CELERY_BROKER_URL: str | None = None
    CELERY_SENTINEL_MASTER_NAME: str | None = None
    CELERY_SENTINEL_SOCKET_TIMEOUT: PositiveFloat = 1

    @computed_field
    def CELERY_RESULT_BACKEND(self) -> str | None:
        return (
            "db+{}".format(self.SQLALCHEMY_DATABASE_URI)
            if self.CELERY_BACKEND == "database"
            else self.CELERY_BROKER_URL
        )

    @property
    def BROKER_USE_SSL(self) -> bool:
        return self.CELERY_BROKER_URL.startswith("rediss://") \
            if self.CELERY_BROKER_URL else False
