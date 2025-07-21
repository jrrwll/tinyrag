from typing import Generator

from opendal import Operator

from app.config import settings
from app.core.file.storage.base import FileEntry, StorageProvider


class OpendalStorageProvider(StorageProvider):

    client: Operator

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

    def list_files(self, prefix: str, recursive: bool = False) -> Generator[
        FileEntry, None, None]:
        entries = self.client.list(prefix, recursive=recursive)
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
                )

    def download_file(self, key: str, local_path: str) -> None:
        data = self.client.read(key)
        with open(local_path, "wb") as f:
            self.client.read()
            f.write(data)

    def upload_file(self, key: str, local_path: str) -> None:
        with open(local_path, "rb") as f:
            while chunk := f.read(8 << 20): # 8M buf
                self.client.write(key, chunk)
