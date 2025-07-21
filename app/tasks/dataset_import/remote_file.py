import logging
import os
import os.path
from uuid import uuid4

from app.config import settings
from app.core.dataset.api import DatasetPublic
from app.core.dataset.process_rule import get_text_splitter
from app.core.file.enums import FileType
from app.core.file.service.file_type import detect_file_type
from app.core.file.service.load import load_document_file
from app.core.file.storage.base import get_storage_provider
from app.core.task.service import update_task_progress
from app.tasks.dataset_import import save_documents
from app.util.datetme import format_date_compact

logger = logging.getLogger(__name__)


def import_remote_files(
        task_id: str, dataset: DatasetPublic, remote_files: list[str]):
    process_rule = dataset.process_rule
    text_splitter = get_text_splitter(process_rule)
    storage_provider = get_storage_provider()

    task_raito, task_raito_step = 0.0, 1 / len(remote_files)
    file_dir = _get_local_dir()
    for file_key in remote_files:
        local_path = f"{file_dir}/{uuid4()}"
        storage_provider.download_file(file_key, local_path)

        file_type = detect_file_type(local_path)
        if not file_type:
            logger.warning(f"skip {file_key} since file_type={file_type}")
            task_raito += task_raito_step
            continue
        file_type, _ = file_type

        docs = load_document_file(local_path, file_type)
        save_documents(docs, text_splitter, dataset)

        task_raito += task_raito_step
        progress = int(task_raito * 100)
        if not update_task_progress(task_id, progress):
            logger.warning(f"async_task={task_id}, "
                           f"update task progress={progress} failed")


def _get_local_dir() -> str:
    file_dir = f"{settings.UPLOAD_DIRECTORY}/{format_date_compact()}"
    if not os.path.exists(file_dir):
        os.makedirs(file_dir, exist_ok=True)
    return file_dir
