import json
import logging
from typing import Iterable

from app.api.model import get_default_model
from app.core.file.service.upload import get_file_path
from app.core.model.api import ModelPublic
from app.core.model.enums import ModelType
from app.core.rag.api import DatasetImportFile, \
    DatasetPublic
from app.core.rag.enums import DocumentSourceType
from app.core.rag.text_process.base import get_text_processor
from app.core.rag.vector.base import VectorFactory
from app.core.task.service import update_task_progress
from app.entities.dataset import Dataset
from app.entities.file import File
from app.tasks.dataset_import import import_documents
from app.tasks.dataset_import.base import FileTaskParams

logger = logging.getLogger(__name__)


def import_files(
        task_id: str, file: DatasetImportFile, dataset: DatasetPublic,
        files: dict[str, File]):
    process_rule = dataset.process_rule
    text_processor = get_text_processor(process_rule)

    collection_name = Dataset.get_collection_name(dataset.id)
    model = get_default_model(ModelType.TextEmbedding)
    vector = VectorFactory.create_vector(collection_name,
                                         ModelPublic.create(model))

    file_ids = file.file_ids
    task_raito, task_raito_step = 0.0, 1 / len(file_ids)
    for file_id in file_ids:
        file = files[file_id]

        file_path = get_file_path(file.id)
        docs = text_processor.load_documents(file_path, file.type)

        source_info = json.dumps({"file_id": file_id})
        import_documents(docs, text_processor, dataset,
                         DocumentSourceType.Upload, source_info)

        task_raito += task_raito_step
        progress = int(task_raito * 100)
        if not update_task_progress(task_id, progress):
            logger.warning(f"async_task={task_id}, "
                           f"update task progress={progress} failed")


def list_files(file: DatasetImportFile,
        files: dict[str, File]) -> Iterable[FileTaskParams]:
    file_ids = file.file_ids
    for file_id in file_ids:
        file = files[file_id]
        file_path = get_file_path(file.id)

        source_info = json.dumps({"file_id": file_id})

        yield FileTaskParams(
            file_path=file_path, file_type=file.type,
            source_info=source_info, source_type=DocumentSourceType.Upload)
