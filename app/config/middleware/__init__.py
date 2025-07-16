from pydantic import (
    MySQLDsn,
    computed_field,
)
from pydantic_settings import BaseSettings

from app.config.middleware.celery import CeleryConfig
from app.config.middleware.redis import RedisConfig


class DatabaseConfig(BaseSettings):

    DB_URI_SCHEME: str = "mysql+pymysql" # or postgresql
    DB_HOST: str = 'locahost'
    DB_PORT: int = 3306
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_DATABASE: str = "tinyrag"
    DB_EXTRAS: str = ""

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return str(MySQLDsn.build(
            scheme=self.DB_URI_SCHEME,
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            path=self.DB_DATABASE,
            query=self.DB_EXTRAS),
        )


class MiddlewareConfig(
    DatabaseConfig,
    RedisConfig,
    CeleryConfig,
):
    pass
