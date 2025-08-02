from uuid import uuid4

from sqlmodel import select

from app.common.deps import open_session
from app.core.file.service.base import get_storage_files
from app.core.knowledge.api import KnowledgePublic
from app.core.model.enums import ModelType
from app.core.task.enums import AsyncTaskStatus, AsyncTaskType
from app.entities.dao.knowledge import get_knowledge
from app.entities.file import File
from app.entities.repo.model import get_required_setup_model
from app.entities.repo.vector_store import get_setup_vector_store
from app.entities.task import AsyncTask
from app.tasks.knowledge_import import import_from_files
from app.tasks.knowledge_import.file import list_files
from app.tasks.knowledge_import.storage import list_storage_files


def test_list_files():
    print("\ntest_list_files")
    with open_session() as session:
        select_stmt = select(File).where(File.tenant_id == 1).limit(10)

        files = session.exec(select_stmt).all()
        file_dict = {file.id: file for file in files}

    for params in list_files(file_dict):
        print(params.model_dump_json())


def test_list_storage_files():
    print("\ntest_list_storage_files")
    storage_files = get_storage_files("chinese-poetry/quantangshi/")

    limit = 10
    for params in list_storage_files(storage_files):
        print(params.model_dump_json())
        limit -= 1
        if limit == 0:
            break


def test_knowledge_import_task_for_storage_files():
    print("\ntest_storage_files")
    workspace_id, tenant_id = 1, 1
    knowledge_id = 1

    with open_session() as session:
        knowledge = get_knowledge(session, knowledge_id, tenant_id)
        if not knowledge:
            print("knowledge not found")
            return
        vector_store = get_setup_vector_store(session, workspace_id, tenant_id)
        model = get_required_setup_model(
            session, ModelType.TextEmbedding, workspace_id, tenant_id)

        task_id = str(uuid4())
        entity = AsyncTask(
            id=task_id, type=AsyncTaskType.KnowledgeImport,
            workspace_id=workspace_id, tenant_id=tenant_id,
            ref_id=knowledge.id, payload='{}', status=AsyncTaskStatus.Started)
        session.add(entity)
        session.commit()
        print(f"\ntask_id = {task_id}")

    storage_files = get_storage_files("chinese-poetry/quantangshi/")
    storage_files = storage_files[0:5]

    file_params = list_storage_files(storage_files)
    import_from_files(file_params, len(storage_files), task_id,
                      KnowledgePublic.create(knowledge),
                      model, vector_store)
