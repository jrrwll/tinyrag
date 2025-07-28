from pydantic_settings import SettingsConfigDict

from app.config.api import ApiSettings
from app.config.base import DeploymentSettings, LoggingSettings
from app.config.feature import FeatureSettings
from app.config.middleware import MiddlewareSettings
from app.config.settings_source import SettingsSourceSettings


class Settings(
    ApiSettings,
    DeploymentSettings,
    LoggingSettings,
    MiddlewareSettings,
    FeatureSettings,
    SettingsSourceSettings,
):
    model_config = SettingsConfigDict(
        # .env in the root dir of the project
        env_file=f"{DeploymentSettings.ROOT_DIR()}/.env",
        env_ignore_empty=True,
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()  # type: ignore
