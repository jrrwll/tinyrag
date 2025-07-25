import json
import logging
from typing import Iterable, Optional
from uuid import uuid4

import orjson
from pydantic import BaseModel

from app.common.db import open_session
from app.common.rq import send_rq_task
from app.core.model.api import ModelPublic
from app.core.model.default_model import get_default_model
from app.core.model.enums import ModelType
from app.core.rag.api import Datase
tImport, DatasetPublic
from app.core.rag.text_process.base import DocumentModel, get_text_processor
from app.core.rag.text_process.keywords import extract_keywords
from app.core.rag.text_process.tokens import get_word_count
from app.core.rag.vector.base import Vector, VectorFactory
from app.core.task.api import AsyncTaskPublic
from app.core.task.service import update_task_progress
from app.entities.dao.dataset import save_document, save_document_chucks
from app.entities.dataset import Dataset, Document as DocumentEntity, \
    DocumentChunk
from app.entities.file import File
from app.entities.task import AsyncTask
from app.tasks.dataset_import.base import FileTaskParams
from app.util.collection import partition_iterable

logger = logging.getLogger(__name__)


class _ImportTaskParams(BaseModel):
    params: DatasetImport
    dataset: DatasetPublic
    files: dict[str, File]
    storage_files: list[str]


def send_dataset_import_task(
        params: DatasetImport, dataset: DatasetPublic,
        files: dict[str, File], storage_files: list[str]) -> AsyncTaskPublic:
    dataset_id = dataset.id
    task_id = str(uuid4())
    with open_session() as session:
        entity = AsyncTask(id=task_id, name=f"dataset_import{dataset_id}",
                           payload=dataset.model_dump_json())
        session.add(entity)
        session.commit()
        session.refresh(entity)

    task_params = _ImportTaskParams(
        params=params,
        dataset=dataset,
        files=files,
        storage_files=storage_files,
    )
    task_params_json = orjson.dumps(task_params.model_dump())

    send_rq_task(task_id, dataset_import_task, task_id, task_params_json)

    return AsyncTaskPublic.new(entity)


# @celery.task(queue="dataset", bind=True, track_started=True)
def dataset_import_task(task_id: str, task_params_json: bytes):
    task_params = _ImportTaskParams.model_validate(
        orjson.loads(task_params_json))
    params = task_params.params
    dataset = task_params.dataset
    files = task_params.files
    storage_files = task_params.storage_files

    if params.file:
        from app.tasks.dataset_import.file import list_files

        file_params = list_files(params.file, files)
        import_from_files(file_params, len(files), task_id, dataset)
    elif params.storage:
        from app.tasks.dataset_import.storage import list_storage_files

        file_params = list_storage_files(storage_files)
        import_from_files(file_params, len(files), task_id, dataset)
    elif params.website:
        from app.tasks.dataset_import.website import import_website

        import_website(task_id, params.website, dataset)


def import_from_files(
        file_params: Iterable[Optional[FileTaskParams]], file_count: int,
        task_id: str, dataset: DatasetPublic):
    process_rule = dataset.process_rule
    text_processor = get_text_processor(process_rule)

    collection_name = Dataset.get_collection_name(dataset.id)
    model = get_default_model(ModelType.TextEmbedding)
    vector = VectorFactory.create_vector(
        collection_name, ModelPublic.create(model))

    task_raito, task_raito_step = 0.0, 1 / file_count
    for params in file_params:
        if not params:
            continue

        docs = text_processor.load_documents(params.file_path, params.file_type)

        position = 0
        for doc in docs:
            doc_entity = DocumentEntity(
                dataset_id=dataset.id, position=position,
                source_type=params.source_type, source_info=params.source_info)
            doc_entity = save_document(doc_entity)

            documents = text_processor.split_documents([doc])

            partition_documents = partition_iterable(documents, 100)
            offset = 0
            for documents in partition_documents:
                import_document_chucks(documents, doc_entity, offset, vector)
                offset += len(documents)

            # update stat fields
            doc_entity.indexing = True
            save_document(doc_entity)
            position += 1

        task_raito += task_raito_step
        progress = int(task_raito * 100)
        if not update_task_progress(task_id, progress):
            logger.warning(f"async_task={task_id}, "
                           f"update task progress={progress} failed")


def import_document_chucks(
        documents: list[DocumentModel], doc_entity: DocumentEntity,
        offset: int, vector: Vector):
    for i in range(len(documents)):
        if not documents[i].id:
            documents[i].id = uuid4()

    vector.add_documents(documents)

    chucks = [to_document_chuck(i + offset, d, doc_entity)
                  for i, d in enumerate(documents)]
    save_document_chucks(chucks)


def to_document_chuck(index: int, doc: DocumentModel,
        doc_entity: DocumentEntity) -> DocumentChunk:
    word_count = get_word_count(doc.page_content)
    keywords = extract_keywords(doc.page_content)
    index_doc_id = doc.id

    doc_entity.word_count += word_count
    return DocumentChunk(
        dataset_id=doc_entity.dataset_id,
        document_id=doc_entity.id,
        position=index,
        content=doc.page_content,
        word_count=word_count,
        keywords=json.dumps(keywords),
        index_doc_id=index_doc_id
    )
