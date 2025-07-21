import logging
import os
import os.path
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Generator
from functools import cache
from pydantic import BaseModel

from app.config import settings
from app.core.file.enums import StorageType
from app.util.metadata import find_sub_types

logger = logging.getLogger(__name__)


class FileEntry(BaseModel):
    key: str  # or prefix for directory
    is_dir: bool = False

    size: int = 0
    last_modified: datetime | None = None
    mime_type: str | None = None


class StorageProvider(ABC):

    @staticmethod
    @abstractmethod
    def get_storage_type() -> StorageType:
        pass

    @abstractmethod
    def test_connect(self) -> None:
        pass

    @abstractmethod
    def exists(self, key_or_prefix: str) -> bool:
        pass

    @abstractmethod
    def list_files(self, prefix: str, recursive: bool = False,
            limit: int | None = None) -> Generator[
        FileEntry, None, None]:
        pass

    @abstractmethod
    def download_file(self, key: str, local_path: str) -> None:
        pass

    @abstractmethod
    def upload_file(self, key: str, local_path: str) -> None:
        pass

    def upload_dir(self, prefix: str, local_dir: str) -> int:
        logger.info(f"Storage upload dir {local_dir} to {prefix}")
        file_count = 0
        for root, _, files in os.walk(local_dir):
            for file in files:
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, local_dir)
                key = os.path.join(prefix, relative_path).replace("\\", "/")

                self.upload_file(key, local_path)
                file_count += 1

        logger.info(f"Finish storage upload dir {local_dir} to {prefix}, total={file_count}")
        return file_count


@cache
def get_storage_provider() -> StorageProvider:
    import app.core.file.storage as _storage

    storage_type = settings.STORAGE_TYPE
    typs = find_sub_types(StorageProvider, _storage)
    for typ in typs:
        if typ.get_storage_type() == storage_type:
            return typ()

    raise AssertionError("StorageProvider")
