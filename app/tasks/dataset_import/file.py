import json
import logging

from app.core.rag.api import DatasetImportFile, \
    DatasetPublic
from app.core.rag.text_process.base import get_text_splitter
from app.core.file.service.load import load_document_file
from app.core.file.service.upload import get_file_path
from app.core.rag.enums import DocumentSourceType
from app.core.task.service import update_task_progress
from app.entities.file import File
from app.tasks.dataset_import import import_documents

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

        source_info = json.dumps({"file_id": file_id})
        import_documents(docs, text_splitter, dataset,
                         DocumentSourceType.Upload, source_info)

        task_raito += task_raito_step
        progress = int(task_raito * 100)
        if not update_task_progress(task_id, progress):
            logger.warning(f"async_task={task_id}, "
                           f"update task progress={progress} failed")
