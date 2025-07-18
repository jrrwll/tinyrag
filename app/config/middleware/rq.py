from pydantic_settings import BaseSettings


class RqConfig(BaseSettings):

    RQ_REDIS_URL: str = "redis://localhost:6379/0"
    RQ_DEQUEUE_STRATEGY: str | None = None
