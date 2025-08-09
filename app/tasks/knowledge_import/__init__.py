import logging
from uuid import uuid4

import orjson
from pydantic import BaseModel

from app.common.deps import open_session
from app.core.knowledge.api import KnowledgePublic
from app.core.knowledge.base import ProcessRule
from app.core.model.api import ModelPublic
from app.core.storage.api import StoragePublic
from app.core.storage.provider.base import StorageProviderFactory
from app.core.task.api import AsyncTaskPublic
from app.core.task.enums import AsyncTaskType
from app.core.vector_store.api import VectorStorePublic
from app.entities.file import File
from app.entities.task import AsyncTask
from app.tasks.base import send_rq_task
from app.tasks.knowledge_import.base import _FileTaskParams, import_from_files

logger = logging.getLogger(__name__)


class ImportTaskParams(BaseModel):
    tenant_id: int
    workspace_id: int
    knowledge: KnowledgePublic
    model: ModelPublic
    vector_store: VectorStorePublic
    storage: StoragePublic | None = None

    process_rule: ProcessRule
    files: dict[str, File] | None = None
    storage_files: list[str] | None = None


def send_knowledge_import_task(
        task_params: ImportTaskParams) -> AsyncTaskPublic:
    task_params_json = orjson.dumps(task_params.model_dump()).decode('utf-8')

    task_id = str(uuid4())
    with open_session() as session:
        entity = AsyncTask(
            id=task_id, type=AsyncTaskType.KnowledgeImport,
            workspace_id=task_params.workspace_id,
            tenant_id=task_params.tenant_id,
            ref_id=task_params.knowledge.id, payload=task_params_json)
        session.add(entity)
        session.commit()
        session.refresh(entity)

    send_rq_task(task_id, knowledge_import_task, task_id, task_params_json)
    return AsyncTaskPublic.create(entity)


# @celery.task(queue="knowledge", bind=True, track_started=True)
def knowledge_import_task(task_id: str, task_params_json: str | bytes):
    logger.info(f"received task {task_id}: {task_params_json}")
    task_params = ImportTaskParams.model_validate_json(task_params_json)

    tenant_id, workspace_id = task_params.tenant_id, task_params.workspace_id
    knowledge = task_params.knowledge
    model, vector_store = task_params.model, task_params.vector_store

    process_rule = task_params.process_rule
    files = task_params.files
    storage_files = task_params.storage_files

    if files:
        from app.tasks.knowledge_import.file import list_file_tasks

        file_params = list_file_tasks(files)
        import_from_files(
            file_params, len(files), knowledge, process_rule,
            model, vector_store, task_id, tenant_id, workspace_id)
    elif storage_files:
        from app.tasks.knowledge_import.storage import list_storage_file_tasks

        storage_provider = StorageProviderFactory.create_storage(task_params.storage)
        file_params = list_storage_file_tasks(storage_files, storage_provider)
        import_from_files(
            file_params, len(storage_files), knowledge, process_rule,
            model, vector_store, task_id, tenant_id, workspace_id)
