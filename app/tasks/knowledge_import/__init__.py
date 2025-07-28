from uuid import uuid4

import orjson
from pydantic import BaseModel

from app.common.db import open_session
from app.common.rq import send_rq_task
from app.core.rag.api import KnowledgeImport, KnowledgePublic
from app.core.task.api import AsyncTaskPublic
from app.core.task.enums import AsyncTaskType
from app.entities.file import File
from app.entities.task import AsyncTask
from app.tasks.knowledge_import.base import _FileTaskParams, import_from_files
from app.util.model import dump_json

class _ImportTaskParams(BaseModel):
    params: KnowledgeImport
    knowledge: KnowledgePublic
    files: dict[str, File]
    storage_files: list[str]


def send_knowledge_import_task(
        params: KnowledgeImport, knowledge: KnowledgePublic,
        files: dict[str, File], storage_files: list[str]) -> AsyncTaskPublic:
    knowledge_id = knowledge.id
    task_id = str(uuid4())
    task_params = _ImportTaskParams(
        params=params,
        knowledge=knowledge,
        files=files,
        storage_files=storage_files,
    )
    # task_params_json = orjson.dumps(task_params.model_dump())
    task_params_json = dump_json(task_params.model_dump())

    with open_session() as session:
        entity = AsyncTask(
            id=task_id, type=AsyncTaskType.KnowledgeImport,
            ref_id=knowledge_id, payload=task_params_json)
        session.add(entity)
        session.commit()
        session.refresh(entity)

    send_rq_task(task_id, knowledge_import_task, task_id, task_params_json)

    return AsyncTaskPublic.new(entity)


# @celery.task(queue="knowledge", bind=True, track_started=True)
def knowledge_import_task(task_id: str, task_params_json: bytes):
    task_params = _ImportTaskParams.model_validate(
        orjson.loads(task_params_json))
    params = task_params.params
    knowledge = task_params.knowledge
    files = task_params.files
    storage_files = task_params.storage_files

    if params.file:
        from app.tasks.knowledge_import.file import list_files

        file_params = list_files(files)
        import_from_files(file_params, len(files), task_id, knowledge)
    elif params.storage:
        from app.tasks.knowledge_import.storage import list_storage_files

        file_params = list_storage_files(storage_files)
        import_from_files(file_params, len(files), task_id, knowledge)
    elif params.website:
        from app.tasks.knowledge_import.website import import_website

        import_website(task_id, params.website, knowledge)
