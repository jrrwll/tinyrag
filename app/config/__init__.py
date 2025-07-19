from pydantic_settings import SettingsConfigDict

from app.config.api import ApiConfig
from app.config.base import DeploymentConfig, LoggingConfig
from app.config.feature import FeatureConfig
from app.config.middleware import MiddlewareConfig
from app.config.settings_source import SettingsSourceConfig


class Settings(
    ApiConfig,
    DeploymentConfig,
    LoggingConfig,
    MiddlewareConfig,
    FeatureConfig,
    SettingsSourceConfig,
):
    model_config = SettingsConfigDict(
        # .env in the root dir of the project
        env_file=f"{DeploymentConfig.ROOT_DIR()}/.env",
        env_ignore_empty=True,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()  # type: ignore
