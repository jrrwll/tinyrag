import logging

from app.core.dataset.api import DatasetImportFile, \
    DatasetPublic
from app.core.dataset.process_rule import get_text_splitter
from app.core.file.service.load import load_document_file
from app.core.task.service import update_task_progress
from app.entities.dao.dataset import save_document, save_document_chucks
from app.entities.dataset import Document as DocumentEntity
from app.entities.file import File
from app.tasks.dataset_import import to_document_chuck

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

        docs = load_document_file(file)
        position = 0
        for doc in docs:
            doc_entity = DocumentEntity(dataset_id=dataset.id,
                                        position=position, file_id=file_ids)
            doc_entity = save_document(doc_entity)

            documents = text_splitter.split_documents([doc])

            chucks = [to_document_chuck(i, d, doc_entity)
                      for i, d in enumerate(documents)]
            save_document_chucks(chucks)

            # update stat fields
            save_document(doc_entity)

            position += 1

        task_raito += task_raito_step
        progress = int(task_raito * 100)
        if not update_task_progress(task_id, progress):
            logger.warning(f"async_task={task_id}, "
                           f"update task progress={progress} failed")
