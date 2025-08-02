from uuid import uuid4

import orjson
from pydantic import BaseModel

from app.common.deps import open_session
from app.common.rq import send_rq_task
from app.core.knowledge.api import KnowledgePublic
from app.core.model.api import ModelPublic
from app.core.task.api import AsyncTaskPublic
from app.core.task.enums import AsyncTaskType
from app.core.vector_store.api import VectorStorePublic
from app.entities.file import File
from app.entities.task import AsyncTask
from app.tasks.knowledge_import.base import _FileTaskParams, import_from_files


class ImportTaskParams(BaseModel):
    knowledge: KnowledgePublic
    model: ModelPublic
    vector_store: VectorStorePublic

    files: dict[str, File] | None = None
    storage_files: list[str] | None = None
    page_urls: list[str] | None = None


def send_knowledge_import_task(
        task_params: ImportTaskParams, workspace_id: int, tenant_id: int
) -> AsyncTaskPublic:
    task_params_json = orjson.dumps(task_params.model_dump()).decode('utf-8')

    task_id = str(uuid4())
    with open_session() as session:
        entity = AsyncTask(
            id=task_id, type=AsyncTaskType.KnowledgeImport,
            workspace_id=workspace_id, tenant_id=tenant_id,
            ref_id=task_params.knowledge.id, payload=task_params_json)
        session.add(entity)
        session.commit()
        session.refresh(entity)

    send_rq_task(task_id, knowledge_import_task, task_id, task_params_json)
    return AsyncTaskPublic.create(entity)


# @celery.task(queue="knowledge", bind=True, track_started=True)
def knowledge_import_task(task_id: str, task_params_json: str | bytes):
    # task_params = ImportTaskParams.model_validate(
    #     orjson.loads(task_params_json))
    task_params = ImportTaskParams.model_validate_json(task_params_json)

    knowledge = task_params.knowledge
    model, vector_store = task_params.model, task_params.vector_store
    files = task_params.files
    storage_files = task_params.storage_files
    page_urls = task_params.page_urls

    if files:
        from app.tasks.knowledge_import.file import list_files

        file_params = list_files(files)
        import_from_files(file_params, len(files), task_id, knowledge, model,
                          vector_store)
    elif storage_files:
        from app.tasks.knowledge_import.storage import list_storage_files

        file_params = list_storage_files(storage_files)
        import_from_files(file_params, len(storage_files), task_id, knowledge,
                          model, vector_store)
    elif page_urls:
        from app.tasks.knowledge_import.website import import_website

        import_website(task_id, page_urls, knowledge)
