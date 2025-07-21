import logging
from uuid import uuid4

from app.config import settings
from app.core.dataset.api import DatasetImportFile, \
    DatasetImportRemoteFile, DatasetPublic
from app.core.dataset.process_rule import get_text_splitter
from app.core.file.service.load import load_document_file
from app.core.file.storage.base import get_storage_provider
from app.core.task.service import update_task_progress
from app.entities.dao.dataset import save_document, save_document_chucks
from app.entities.dataset import Document as DocumentEntity
from app.entities.file import File
from app.tasks.dataset_import import to_document_chuck
import os.path
import os

from app.util.datetme import format_date_compact

logger = logging.getLogger(__name__)


def import_remote_files(
        task_id: str, remote_file: DatasetImportRemoteFile,
        dataset: DatasetPublic, remote_files: list[str]):
    process_rule = dataset.process_rule
    text_splitter = get_text_splitter(process_rule)
    storage_provider = get_storage_provider()

    task_raito, task_raito_step = 0.0, 1 / len(remote_files)
    file_dir = _get_local_dir()
    for remote_file in remote_files:
        local_path = f"{file_dir}/{uuid4()}"
        storage_provider.download_file(remote_file, local_path)
        docs = load_document_file(local_path)


def _get_local_dir() -> str:
    file_dir = f"{settings.UPLOAD_DIRECTORY}/{format_date_compact()}"
    if not os.path.exists(file_dir):
        os.makedirs(file_dir, exist_ok=True)
    return file_dir
