import logging

from app.core.dataset.api import DatasetImportFile, \
    DatasetPublic
from app.core.dataset.process_rule import get_text_splitter
from app.core.file.service.load import load_document_file
from app.core.file.service.upload import get_file_path
from app.core.task.service import update_task_progress
from app.entities.file import File
from app.tasks.dataset_import import save_documents

logger = logging.getLogger(__name__)


def import_files(
        task_id: str, file: DatasetImportFile, dataset: DatasetPublic,
        files: dict[str, File]):
    process_rule = dataset.process_rule
    text_splitter = get_text_splitter(process_rule)

    file_ids = file.file_ids

    task_raito, task_raito_step = 0.0, 1 / len(file_ids)
    for file_id in file_ids:
        file = files[file_id]

        file_path = get_file_path(file.id)
        docs = load_document_file(file_path, file.type)

        save_documents(docs, text_splitter, dataset, file_id)

        task_raito += task_raito_step
        progress = int(task_raito * 100)
        if not update_task_progress(task_id, progress):
            logger.warning(f"async_task={task_id}, "
                           f"update task progress={progress} failed")
