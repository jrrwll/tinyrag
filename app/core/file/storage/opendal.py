import logging
from typing import Generator

from opendal import Operator

from app.config import settings
from app.core.file.enums import StorageType
from app.core.file.storage.base import FileEntry, StorageProvider

logger = logging.getLogger(__name__)


class OpendalStorageProvider(StorageProvider):
    client: Operator

    @staticmethod
    def get_storage_type() -> StorageType:
        return StorageType.Opendal

    def __init__(self):
        if settings.OPENDAL_SCHEME == "fs":
            self.client = Operator(
                "fs", root=settings.opendal_local_path
            )
        else:
            options = {
                "endpoint": settings.OPENDAL_ENDPOINT,
                "region": settings.OPENDAL_REGION,
                "access_key_id": settings.OPENDAL_ACCESS_KEY,
                "secret_access_key": settings.OPENDAL_SECRET_KEY,
                "bucket": settings.OPENDAL_BUCKET_NAME,
            }
            options = {k: v for k, v in options.items() if v}
            self.client = Operator(settings.OPENDAL_SCHEME, **options)

    def test_connect(self) -> None:
        entries = self.client.list("/", limit=1)
        next(iter(entries), [])

    def exists(self, key_or_prefix: str) -> bool:
        return self.client.exists(key_or_prefix)

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
