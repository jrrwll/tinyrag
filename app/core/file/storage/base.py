import logging
import os
import os.path
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Generator

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class FileEntry(BaseModel):
    key: str  # or prefix for directory
    is_dir: bool = False

    size: int = 0
    last_modified: datetime | None = None


class StorageProvider(ABC):

    @abstractmethod
    def test_connect(self) -> None:
        pass

    @abstractmethod
    def list_files(self, prefix: str, recursive: bool = False) -> Generator[
        FileEntry, None, None]:
        pass

    @abstractmethod
    def download_file(self, key: str, local_path: str) -> None:
        pass

    @abstractmethod
    def upload_file(self, key: str, local_path: str) -> None:
        pass

    def upload_dir(self, prefix: str, local_dir: str) -> int:
        file_count = 0
        for root, _, files in os.walk(local_dir):
            for file in files:
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, local_dir)
                key = os.path.join(prefix, relative_path).replace("\\", "/")

                logger.info("upload {local_path} to {key}")
                self.upload_file(key, local_path)
                file_count += 1

        return file_count
