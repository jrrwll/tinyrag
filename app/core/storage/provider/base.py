import logging
import os
import os.path
import threading
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Generator

from cachetools import TTLCache
from pydantic import BaseModel

from app.core.meta.provider import ProviderMetaService
from app.core.storage.api import StoragePublic
from app.core.storage.enums import StorageType

logger = logging.getLogger(__name__)


class FileEntry(BaseModel):
    key: str  # or prefix for directory
    is_dir: bool = False

    size: int = 0
    last_modified: datetime | None = None
    mime_type: str | None = None


class StorageProvider[Cfg: BaseModel, C](ABC):
    _lock = threading.Lock()

    @staticmethod
    @abstractmethod
    def get_storage_type() -> StorageType:
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def get_config_type() -> type[Cfg]:
        raise NotImplementedError()

    @classmethod
    def validate_config(cls, config: dict):
        cls.get_config_type().model_validate(config)

    @abstractmethod
    def _create_client(self) -> C:
        raise NotImplementedError()

    def __init__(self, storage: StoragePublic):
        ProviderMetaService.from_storage().decrypt_config_dict(
            storage.type, storage.config)
        self.config = self.get_config_type()(**storage.config)
        self._footprint: str = storage.footprint()
        self._storage_local_dir = storage.local_dir()
        self._init()

    def _init(self) -> None:
        with self._lock:
            client = _client_cache.get(self._footprint)
            if client:
                self.client = client
                # renewal ttl
                _client_cache[self._footprint] = client
            else:
                self.client = self._create_client()
                _client_cache[self._footprint] = self.client

    @abstractmethod
    def test_connect(self) -> None:
        raise NotImplementedError()

    def exists(self, key_or_prefix: str) -> bool:
        return self.metadata(key_or_prefix) is not None

    @abstractmethod
    def metadata(self, key_or_prefix: str) -> FileEntry | None:
        raise NotImplementedError()

    @abstractmethod
    def list_files(self, prefix: str,
            recursive: bool = False, limit: int | None = None
    ) -> Generator[FileEntry, None, None]:
        raise NotImplementedError()

    @abstractmethod
    def download_file(self, key: str, local_path: str) -> None:
        raise NotImplementedError()

    @abstractmethod
    def upload_file(self, key: str, local_path: str) -> None:
        raise NotImplementedError()

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


_client_cache: TTLCache[str, Any] = TTLCache(
    maxsize=1000, ttl=10 * 60)  # 10min


class StorageProviderFactory:

    @classmethod
    def create_storage(
            cls, storage: StoragePublic
    ) -> StorageProvider:
        provider_class = cls.get_provider_class(storage.type)
        return provider_class(storage)

    @staticmethod
    def get_provider_class[T: StorageProvider](
            vector_store_type: StorageType) -> type[T]:
        if vector_store_type == StorageType.S3:
            from app.core.storage.provider.s3 import S3StorageProvider

            return S3StorageProvider
        else:
            from app.cor

            e.storage.provider.opendal import OpendalStorageProvider

            return OpendalStorageProvider
