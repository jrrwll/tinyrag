import logging

import orjson
from langchain_core.documents import Document
from pydantic import BaseModel

from app.common.db import open_session
from app.common.scheduler import send_rq_task
from app.core.dataset.api import DatasetImport, DatasetImportFile, \
    DatasetImportWebsite, DatasetPublic
from app.core.dataset.process_rule import get_text_splitter
from app.core.file.service.load import load_document_file
from app.core.task.api import AsyncTaskPublic
from app.core.task.service import update_task_progress
from app.entities.dao.dataset import save_document, save_document_chucks
from app.entities.dataset import Document as DocumentEntity, DocumentChunk
from app.entities.file import File
from app.entities.task import AsyncTask

logger = logging.getLogger(__name__)


class ImportTaskParams(BaseModel):
    params: DatasetImport
    dataset: DatasetPublic
    files: dict[str, File]


def send_dataset_import_task(
        params: DatasetImport, dataset: DatasetPublic,
        files: dict[str, File]) -> AsyncTaskPublic:
    dataset_id = dataset.id
    with open_session() as session:
        entity = AsyncTask(name=f"dataset_import{dataset_id}",
                           payload=dataset.model_dump_json())
        session.add(entity)
        session.commit()
        session.refresh(entity)

    task_id = str(entity.id)
    task_params = ImportTaskParams(
        params=params,
        dataset=dataset,
        files=files,
    )
    task_params_json = orjson.dumps(task_params.model_dump())

    send_rq_task(task_id, dataset_import_task, task_id, task_params_json)

    return AsyncTaskPublic.new(entity)


# @celery.task(queue="dataset", bind=True, track_started=True)
def dataset_import_task(task_id: str, task_params_json: bytes):
    task_params = ImportTaskParams.model_validate(
        orjson.loads(task_params_json))
    params = task_params.params
    dataset = task_params.dataset
    files = task_params.files

    if params.file:
        _import_files(task_id, params.file, dataset, files)
    elif params.website:
        _import_website(task_id, params.website, dataset)


def _import_files(
        task_id: str, file: DatasetImportFile, dataset: DatasetPublic,
        files: dict[str, File]):
    process_rule = dataset.process_rule
    text_splitter = get_text_splitter(process_rule)

    file_ids = file.file_ids
    file_count = len(file_ids)

    task_raito, task_raito_step = 0.0, 1 / file_count
    for i in range(file_count):
        file_id = file_ids[i]
        file = files[file_id]

        docs = load_document_file(file)
        position = 0
        for doc in docs:
            doc_entity = DocumentEntity(dataset_id=dataset.id,
                                        position=position, file_id=file_ids)
            doc_entity = save_document(doc_entity)

            documents = text_splitter.split_documents([doc])

            chucks = [_to_document_chuck(i, d, doc_entity)
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


def _import_website(
        task_id: str, file: DatasetImportWebsite,
        dataset: DatasetPublic):
    pass


def _to_document_chuck(index: int, doc: Document,
        doc_entity: DocumentEntity) -> DocumentChunk:
    word_count = len(doc.page_content.split())
    doc_entity.word_count += word_count
    return DocumentChunk(
        dataset_id=doc_entity.dataset_id,
        document_id=doc_entity.id,
        position=index,
        content=doc.page_content,
        word_count=word_count,
        keywords=doc.metadata.get("keywords", ""),
        created_at=doc_entity.created_at,
        updated_at=doc_entity.updated_at,
    )
