import os
from uuid import uuid4

from app.common.error_code import BizException, ErrorCode
from app.config import settings
from app.core.storage.provider.base import StorageProvider
from corepy.datetime import format_date_compact


def download_storage_file(file_key: str,
        storage_provider: StorageProvider) -> str:
    file_dir = f"{settings.UPLOAD_DIRECTORY}/{format_date_compact()}"
    if not os.path.exists(file_dir):
        os.makedirs(file_dir, exist_ok=True)

    local_path = f"{file_dir}/{uuid4()}"
    storage_provider.download_file(file_key, local_path)
    return local_path


def list_storage_files(
        file_path: str, storage_provider: StorageProvider
) -> list[str]:
    metadata = storage_provider.metadata(file_path)
    if not metadata:
        raise BizException.create(ErrorCode.storage_file_not_found)

    if not metadata.is_dir:
        return [file_path]

    files = storage_provider.list_files(
        file_path, recursive=True,
        limit=settings.STORAGE_LIST_FILE_MAX_COUNT)

    keys = [file.key for file in files if not file.is_dir]
    if not keys:
        raise BizException.create(ErrorCode.storage_file_not_found)
    return keys
