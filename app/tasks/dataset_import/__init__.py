from uuid import uuid4

import orjson
from langchain_core.documents import Document
from pydantic import BaseModel

from app.common.db import open_session
from app.common.rq import send_rq_task
from app.core.dataset.api import DatasetImport, DatasetPublic
from app.core.task.api import AsyncTaskPublic
from app.entities.dao.dataset import save_document, save_document_chucks
from app.entities.dataset import Document as DocumentEntity, DocumentChunk
from app.entities.file import File
from app.entities.task import AsyncTask


class _ImportTaskParams(BaseModel):
    params: DatasetImport
    dataset: DatasetPublic
    files: dict[str, File]
    remote_files: list[str]


def send_dataset_import_task(
        params: DatasetImport, dataset: DatasetPublic,
        files: dict[str, File], remote_files: list[str]) -> AsyncTaskPublic:
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
        remote_files=remote_files,
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
    remote_files = task_params.remote_files

    if params.file:
        from app.tasks.dataset_import.file import import_files

        import_files(task_id, params.file, dataset, files)
    elif params.remote_file:
        from app.tasks.dataset_import.remote_file import import_remote_files

        import_remote_files(task_id, params.remote_file, dataset, remote_files)
    elif params.website:
        from app.tasks.dataset_import.website import import_website

        import_website(task_id, params.website, dataset)



# FIXME
def save_documents(dataset: DatasetPublic):
    position = 0
    for doc in docs:
        doc_entity = DocumentEntity(
            dataset_id=dataset_id,
            position=position, file_id=file_ids)
        doc_entity = save_document(doc_entity)

        documents = text_splitter.split_documents([doc])

        chucks = [to_document_chuck(i, d, doc_entity)
                  for i, d in enumerate(documents)]
        save_document_chucks(chucks)

        # update stat fields
        save_document(doc_entity)

        position += 1

def to_document_chuck(index: int, doc: Document,
        doc_entity: DocumentEntity) -> DocumentChunk:
    word_count = len(doc.page_content.split())
    doc_entity.word_count += word_count
    return DocumentChunk(
        dataset_id=doc_entity.dataset_id,
        document_id=doc_entity.id,
        position=index,
        content=doc.page_content,
        word_count=word_count,
    )

