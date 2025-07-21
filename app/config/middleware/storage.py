from pydantic_settings import BaseSettings

from app.common.constants import APP_NAME
from app.config.base import _singleton_workdir
from app.core.file.enums import StorageType


class StorageConfig(BaseSettings):
    STORAGE_TYPE: StorageType = StorageType.Opendal
    STORAGE_LIST_FILE_MAX_COUNT: int = 1000

    OPENDAL_SCHEME: str = "fs"
    OPENDAL_LOCAL_PATH: str | None = None
    OPENDAL_ENDPOINT: str | None = None
    OPENDAL_REGION: str | None = None
    OPENDAL_ACCESS_KEY: str | None = None
    OPENDAL_SECRET_KEY: str | None = None
    OPENDAL_BUCKET_NAME: str | None = APP_NAME

    S3_ENDPOINT: str | None = None
    S3_REGION: str | None = None
    S3_BUCKET_NAME: str | None = APP_NAME
    S3_ACCESS_KEY: str | None = None
    S3_SECRET_KEY: str | None = None

    @property
    def opendal_local_path(self):
        if self.OPENDAL_LOCAL_PATH:
            return self.OPENDAL_LOCAL_PATH
        return f"{_singleton_workdir}/opendal"
