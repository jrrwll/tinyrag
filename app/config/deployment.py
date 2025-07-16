from pathlib import Path
from typing import Literal

from pydantic import (
    computed_field,
)
from pydantic_settings import BaseSettings

_root_dir = str(Path(__file__).resolve().parents[2])

_singleton_workdir = f"{_root_dir}/workdir"


class DeploymentConfig(BaseSettings):
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
    def ROOT_DIR(cls) -> str:
        return _root_dir
