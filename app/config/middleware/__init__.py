from app.config.middleware.celery import CeleryConfig
from app.config.middleware.db import DatabaseConfig
from app.config.middleware.redis import RedisConfig
from app.config.middleware.rq import RqConfig
from app.config.middleware.storage import StorageConfig


class MiddlewareConfig(
    DatabaseConfig,
    RedisConfig,
    RqConfig,
    CeleryConfig,
    StorageConfig,
):
    pass
