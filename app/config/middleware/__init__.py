from app.config.middleware.celery import CeleryConfig
from app.config.middleware.db import DatabaseConfig
from app.config.middleware.redis import RedisConfig
from app.config.middleware.rq import RqConfig
from app.config.middleware.s3 import S3Config


class MiddlewareConfig(
    DatabaseConfig,
    RedisConfig,
    RqConfig,
    CeleryConfig,
    S3Config,
):
    pass
