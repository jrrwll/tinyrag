import json
import logging
from typing import Iterable, Optional

from app.core.file.service.upload import get_file_path
from app.core.rag.enums import DocumentSourceType
from app.entities.file import File
from app.tasks.dataset_import.base import _FileTaskParams

logger = logging.getLogger(__name__)


def list_files(files: dict[str, File]) -> Iterable[Optional[_FileTaskParams]]:
    for file_id, file in files.items():
        file = files[file_id]
        file_path = get_file_path(file.id)

        source_info = json.dumps({"file_id": file_id})

        yield _FileTaskParams(
            file_path=file_path, file_type=file.type,
            source_info=source_info, source_type=DocumentSourceType.Upload)
