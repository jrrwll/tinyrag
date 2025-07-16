from pydantic import PositiveInt, Field, NonNegativeInt

from pydantic_settings import BaseSettings


class RedisConfig(BaseSettings):

    REDIS_HOST: str = 'localhost'
    REDIS_PORT: PositiveInt = 6379
    REDIS_USERNAME: str | None = None
    REDIS_PASSWORD: str | None = None
    REDIS_DB: NonNegativeInt = Field(
        description="Redis database number to use (0-15)",
        default=0,
    )
