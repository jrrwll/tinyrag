from pathlib import Path
from typing import Literal

from pydantic import (
    computed_field, PositiveInt
)
from pydantic_settings import BaseSettings

_root_dir = Path(__file__).resolve().parents[2]

_singleton_workdir = _root_dir / "workdir"


class DeploymentSettings(BaseSettings):
    PROJECT_NAME: str
    DEBUG: bool = False

    ENVIRONMENT: Literal["test", "production"] = "test"

    UPLOAD_DIRECTORY: str = f"{_singleton_workdir}/uploads"
    # suggest to use a nfs/oss directory for uploads, for example /nfs/uploads
    FILES_DIRECTORY: str = f"{_singleton_workdir}/files"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def IS_TEST_ENV(self) -> bool:
        return self.ENVIRONMENT == "test"

    @classmethod
    def ROOT_DIR(cls) -> Path:
        return _root_dir


_log_format_prefix = "%(asctime)s %(levelname)s %(requestId)s [%(threadName)s] [%(filename)s:%(lineno)d]"


class LoggingSettings(BaseSettings):

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = f"{_log_format_prefix}: %(message)s"
    LOG_DATEFORMAT: str | None = None
    LOG_TZ: str = "UTC"

    LOG_FILE: str | None = None
    LOG_FILE_MAX_SIZE: PositiveInt = 20 # MB
    LOG_FILE_BACKUP_COUNT: PositiveInt = 10
