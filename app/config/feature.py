from pydantic_settings import BaseSettings
from pydantic import PositiveInt


class LoggingConfig(BaseSettings):

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s.%(msecs)03d %(levelname)s %(requestId)s [%(threadName)s] [%(filename)s:%(lineno)d] - %(message)s"
    LOG_DATEFORMAT: str | None = None
    LOG_TZ: str = "UTC"

    LOG_FILE: str | None = None
    LOG_FILE_MAX_SIZE: PositiveInt = 20 # MB
    LOG_FILE_BACKUP_COUNT: PositiveInt = 10

class ModelConfig(BaseSettings):

    DEFAULT_TEST_PROMPT: str = "Hi!"
    DEFAULT_NODE_OUTPUT_VARIABLE: str = "result"


class FeatureConfig(LoggingConfig, ModelConfig):
    pass
