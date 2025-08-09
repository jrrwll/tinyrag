import json
import logging
from typing import Iterable, Optional

from app.core.file.file_type import detect_file_type
from app.core.knowledge.enums import DocumentSourceType
from app.core.storage.file import download_storage_file
from app.core.storage.provider.base import StorageProvider
from app.tasks.knowledge_import import _FileTaskParams

logger = logging.getLogger(__name__)


def list_storage_file_tasks(
        storage_files: list[str], storage_provider: StorageProvider
) -> Iterable[Optional[_FileTaskParams]]:
    for file_key in storage_files:
        local_path = download_storage_file(file_key, storage_provider)

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
            yield _FileTaskParams(
                file_path=local_path, file_type=file_type,
                source_info=source_info, source_type=DocumentSourceType.Storage)
