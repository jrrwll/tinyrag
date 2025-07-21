from pydantic_settings import BaseSettings

from app.common.constants import APP_NAME
from app.core.file.enums import StorageType


class StorageConfig(BaseSettings):
    STORAGE_TYPE: StorageType = StorageType.Opendal

    OPENDAL_SCHEME: str = "fs"

    S3_ENDPOINT: str | None = None
    S3_REGION: str | None = None
    S3_BUCKET_NAME: str | None = APP_NAME

    S3_ACCESS_KEY: str | None = None
    S3_SECRET_KEY: str | None = None
