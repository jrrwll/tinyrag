from uuid import uuid4

import orjson
from pydantic import BaseModel

from app.common.db import open_session
from app.common.rq import send_rq_task
from app.core.rag.api import DatasetImport, DatasetPublic
from app.core.task.api import AsyncTaskPublic
from app.entities.file import File
from app.entities.task import AsyncTask
from app.tasks.dataset_import.base import _FileTaskParams, import_from_files


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

        file_params = list_files(files)
        import_from_files(file_params, len(files), task_id, dataset)
    elif params.storage:
        from app.tasks.dataset_import.storage import list_storage_files

        file_params = list_storage_files(storage_files)
        import_from_files(file_params, len(files), task_id, dataset)
    elif params.website:
        from app.tasks.dataset_import.website import import_website

        import_website(task_id, params.website, dataset)
