import logging
from typing import Generator, Literal

from opendal import Metadata, Operator
from pydantic import BaseModel, SecretStr, field_validator

from app.common.constants import APP_NAME
from app.config import settings
from app.core.storage.enums import StorageType
from app.core.storage.provider.base import FileEntry, StorageProvider

logger = logging.getLogger(__name__)


class OpendalStorageConfig(BaseModel):
    scheme: Literal["s3"] = "s3"
    endpoint: str
    region: str | None = None
    access_key: SecretStr | None = None
    secret_key: SecretStr | None = None
    bucket_name: str | None = APP_NAME

    @field_validator("endpoint")
    @staticmethod
    def _validate(v: str) -> str:
        if v == '*':
            if not settings.IS_TEST_ENV:
                raise ValueError("endpoint cannot be * in production mode")
        return v


class OpendalStorageProvider(StorageProvider[OpendalStorageConfig, Operator]):

    def _create_client(self) -> Operator:
        if self.config.endpoint == "*":
            return Operator(
                "fs", root=self._storage_local_dir
            )
        else:
            # s3
            options = {
                "endpoint": self.config.endpoint,
                "region": self.config.region,
                "access_key_id": self.config.access_key and self.config.access_key.get_secret_value(),
                "secret_access_key": self.config.secret_key and self.config.secret_key.get_secret_value(),
                "bucket": self.config.bucket_name,
            }
            options = {k: v for k, v in options.items() if v}
            return Operator(self.config.scheme, **options)

    @staticmethod
    def get_storage_type() -> StorageType:
        return StorageType.Opendal

    @staticmethod
    def get_config_type() -> type[OpendalStorageConfig]:
        return OpendalStorageConfig

    def test_connect(self) -> None:
        entries = self.client.list("/", limit=1)
        next(iter(entries), [])

    def exists(self, key_or_prefix: str) -> bool:
        return self.client.exists(key_or_prefix)

    def metadata(self, key_or_prefix: str) -> FileEntry | None:
        if not self.exists(key_or_prefix):
            return None

        metadata: Metadata = self.client.stat(key_or_prefix)
        return FileEntry(
            key=key_or_prefix,
            is_dir=metadata.is_dir,
            size=metadata.content_length,
            last_modified=metadata.last_modified,
            mime_type=metadata.content_type,
        )

    def list_files(self, prefix: str, recursive: bool = False,
            limit: int | None = None) -> Generator[
        FileEntry, None, None]:
        entries = self.client.list(prefix, recursive=recursive, limit=limit)
        for entry in entries:
            key = entry.path
            metadata = entry.metadata
            if metadata.is_dir:
                yield FileEntry(key=key, is_dir=True)
            else:
                yield FileEntry(
                    key=key,
                    size=metadata.content_length,
                    last_modified=metadata.last_modified,
                    mime_type=metadata.content_type,
                )

    def download_file(self, key: str, local_path: str) -> None:
        logger.info(f"Storage download {key} to {local_path}")
        with self.client.open(key, "rb") as r, \
                open(local_path, "wb") as w:
            while chunk := r.read(8 << 20):  # 8M buffer
                w.write(chunk)

    def upload_file(self, key: str, local_path: str) -> None:
        logger.info(f"Storage upload {local_path} to {key}")
        with self.client.open(key, "wb") as w, \
                open(local_path, "rb") as r:
            while chunk := r.read(8 << 20):  # 8M buffer
                w.write(chunk)
