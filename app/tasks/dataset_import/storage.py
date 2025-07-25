import json
import logging
import os
import os.path
from typing import Iterable, Optional
from uuid import uuid4

from app.config import settings
from app.core.file.service.file_type import detect_file_type
from app.core.file.storage.base import get_storage_provider
from app.core.rag.api import DatasetImportStorage
from app.core.rag.enums import DocumentSourceType
from app.tasks.dataset_import import FileTaskParams
from app.util.datetime import format_date_compact

logger = logging.getLogger(__name__)


def list_storage_files(
        storage_files: list[str]) -> Iterable[Optional[FileTaskParams]]:
    storage_provider = get_storage_provider()

    file_dir = _get_local_dir()
    for file_key in storage_files:
        local_path = f"{file_dir}/{uuid4()}"
        storage_provider.download_file(file_key, local_path)

        file_type = detect_file_type(local_path)
        if not file_type:
            logger.warning(f"skip {file_key} since file_type={file_type}")
            yield None
        else:
            file_type, _ = file_type
            source_info = json.dumps({
                "file_key": file_key,
                "file_type": file_type,
            })
            yield FileTaskParams(
                file_path=local_path, file_type=file_type,
                source_info=source_info, source_type=DocumentSourceType.Storage)


def _get_local_dir() -> str:
    file_dir = f"{settings.UPLOAD_DIRECTORY}/{format_date_compact()}"
    if not os.path.exists(file_dir):
        os.makedirs(file_dir, exist_ok=True)
    return file_dir
