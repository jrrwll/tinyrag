import json
from typing import Iterator
from uuid import uuid4

import orjson
from langchain_core.documents import Document
from langchain_text_splitters import TextSplitter
from pydantic import BaseModel

from app.common.db import open_session
from app.common.rq import send_rq_task
from app.core.rag.api import DatasetImport, DatasetPublic
from app.core.rag.enums import DocumentSourceType
from app.core.rag.text_process.keywords import extract_keywords
from app.core.rag.text_process.tokens import get_word_count
from app.core.rag.vectorstores import create_vector_store
from app.core.task.api import AsyncTaskPublic
from app.entities.dao.dataset import save_document, save_document_chucks
from app.entities.dataset import Dataset, Document as DocumentEntity, \
    DocumentChunk
from app.entities.file import File
from app.entities.task import AsyncTask
from app.util.collection import partition_list


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
        from app.tasks.dataset_import.file import import_files

        import_files(task_id, params.file, dataset, files)
    elif params.storage:
        from app.tasks.dataset_import.storage import import_storage_files

        import_storage_files(task_id, dataset, storage_files)
    elif params.website:
        from app.tasks.dataset_import.website import import_website

        import_website(task_id, params.website, dataset)


def import_documents(docs: Iterator[Document], text_splitter: TextSplitter,
        dataset: DatasetPublic,
        source_type: DocumentSourceType, source_info: str):
    position = 0
    for doc in docs:
        doc_entity = DocumentEntity(
            dataset_id=dataset.id, position=position,
            source_type=source_type, source_info=source_info)
        doc_entity = save_document(doc_entity)

        documents = text_splitter.split_documents([doc])

        partition_documents = partition_list(documents)
        offset = 0
        for documents in partition_documents:
            import_document_chucks(documents, doc_entity, offset, dataset)
            offset += len(documents)

        # update stat fields
        doc_entity.indexing = True
        save_document(doc_entity)
        position += 1


def import_document_chucks(documents: list[Document],
        doc_entity: DocumentEntity, offset: int, dataset: DatasetPublic):
    for i in range(len(documents)):
        if not documents[i].id:
            documents[i].id = uuid4()

    collection_name = Dataset.get_collection_name(dataset.id)
    vector_store = create_vector_store(collection_name)
    vector_store.add_documents(documents)

    chucks = [to_document_chuck(i + offset, d, doc_entity)
                  for i, d in enumerate(documents)]
    save_document_chucks(chucks)


def to_document_chuck(index: int, doc: Document,
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
