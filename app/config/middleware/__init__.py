from app.config.middleware.db import DatabaseSettings
from app.config.middleware.redis import RedisSettings
from app.config.middleware.rq import RqSettings
from app.config.middleware.storage import StorageSettings


class MiddlewareSettings(
    DatabaseSettings,
    RedisSettings,
    RqSettings,
    StorageSettings,
):
    pass
