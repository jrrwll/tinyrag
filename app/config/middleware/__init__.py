from app.config.middleware.db import DatabaseSettings
from app.config.middleware.redis import RedisSettings
from app.config.middleware.rq import RqSettings


class MiddlewareSettings(
    DatabaseSettings,
    RedisSettings,
    RqSettings,
):
    pass
