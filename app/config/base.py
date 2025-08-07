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
    DEFAULT_LANG: str = "en"

    ENVIRONMENT: Literal["test", "production"] = "test"

    UPLOAD_DIRECTORY: str = f"{_singleton_workdir}/uploads"
    # suggest to use a nfs/oss directory for uploads, for example /nfs/uploads
    FILES_DIRECTORY: str = f"{_singleton_workdir}/files"
    # for test vector store only
    VECTOR_STORE_DIRECTORY: str = f"{_singleton_workdir}/vectorstore"
    # embedding models
    MODEL_DIRECTORY: str = f"{_singleton_workdir}/models"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def IS_TEST_ENV(self) -> bool:
        return self.ENVIRONMENT == "test"

    @classmethod
    def ROOT_DIR(cls) -> Path:
        return _root_dir


class LoggingSettings(BaseSettings):

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = f"%(asctime)s %(levelname)s %(requestId)s [%(threadName)s] [%(filename)s:%(lineno)d]: %(message)s"
    LOG_DATEFORMAT: str | None = None
    LOG_TZ: str | None = None # example: UTC, Asia/Shanghai

    LOG_FILE: str = f"{_singleton_workdir}/logs/%s.log"
    # LOG_FILE_MAX_SIZE: PositiveInt = 20 # MB
    LOG_FILE_BACKUP_COUNT: PositiveInt = 10
