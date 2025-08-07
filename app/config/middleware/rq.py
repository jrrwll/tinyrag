from pydantic_settings import BaseSettings


class RqSettings(BaseSettings):

    RQ_REDIS_URL: str = "redis://localhost:6379/0"
    RQ_WORKERS: int = 1
