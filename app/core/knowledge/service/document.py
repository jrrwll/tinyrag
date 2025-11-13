from sqlmodel import Session

from app.common.error_code import BizException, ErrorCode
from app.config import settings
from app.core.knowledge.api import KnowledgeDocumentPublic, KnowledgeImport, \
    KnowledgePublic
from app.core.storage.default_storage import get_default_storage
from app.core.storage.file import list_storage_files
from app.core.storage.provider.base import StorageProviderFactory
from app.core.task.api import AsyncTaskPublic
from app.entities.dao.file import get_files
from app.entities.dao.knowledge import get_knowledge, page_and_count_documents
from app.entities.repo.model import get_embedding_model_from_config
from app.entities.repo.vector_store import get_vector_store_from_config
from app.entities.user import User
from app.tasks.knowledge_import import ImportTaskParams, \
    send_knowledge_import_task
from corepy.api import PageResult


def import_documents(session: Session, params: KnowledgeImport,
        current_user: User) -> AsyncTaskPublic:
    tenant_id = current_user.tenant_id
    knowledge_id = params.id

    entity = get_knowledge(session, knowledge_id, tenant_id)
    if not entity:
        raise BizException.create(ErrorCode.knowledge_not_found)
    workspace_id = entity.workspace_id
    knowledge = KnowledgePublic.create(entity)

    model = get_embedding_model_from_config(
        session, knowledge.embedding_model_config, tenant_id)
    vector_store = get_vector_store_from_config(
        session, knowledge.vector_store_config, tenant_id)

    process_rule = params.process_rule
    if not process_rule:
        process_rule = knowledge.process_rule

    task_params = ImportTaskParams(
        tenant_id=tenant_id, workspace_id=workspace_id,
        knowledge=KnowledgePublic.create(entity),
        model=model, vector_store=vector_store,
        process_rule=process_rule,
    )
    # check params
    if params.file:
        file_ids = params.file.file_ids
        task_params.files = get_files(session, file_ids, tenant_id)
        missing_file_ids = [file_id for file_id in file_ids
                            if file_id not in task_params.files]
        if missing_file_ids:
            raise BizException.create(
                ErrorCode.file_ids_not_found, ids=missing_file_ids
            )
    elif params.storage:
        storage = get_default_storage(session, params.storage.storage_id, tenant_id)
        task_params.storage = storage

        storage_provider = StorageProviderFactory.create_storage(storage)
        # todo avoid slow transaction
        task_params.storage_files = list_storage_files(params.storage.file_path, storage_provider)
    else:
        task_params.page_urls = params.website.page_urls

    # import task
    return send_knowledge_import_task(task_params)


def list_documents(
        session: Session, knowledge_id: int,
        page_no: int, page_size: int,
        current_user: User
) -> PageResult[KnowledgeDocumentPublic]:
    tenant_id = current_user.tenant_id

    entities, count = page_and_count_documents(
        session, page_no, page_size,
        knowledge_id, tenant_id)

    return PageResult[KnowledgeDocumentPublic](
        page_no=page_no,
        page_size=page_size,
        total=count,
        items=[KnowledgeDocumentPublic.create(entity) for entity in entities],
    )
