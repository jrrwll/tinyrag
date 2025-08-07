from sqlmodel import Session

from app.common.error_code import BizException, ErrorCode
from app.core.file.service.base import get_storage_files
from app.core.knowledge.api import KnowledgeImport, \
    KnowledgePublic
from app.core.task.api import AsyncTaskPublic
from app.entities.dao.file import get_files
from app.entities.dao.knowledge import get_knowledge
from app.entities.repo.model import get_embedding_model_from_config
from app.entities.repo.vector_store import get_vector_store_from_config
from app.entities.user import User
from app.tasks.knowledge_import import ImportTaskParams, \
    send_knowledge_import_task


def import_documents(session: Session, params: KnowledgeImport,
        current_user: User) -> AsyncTaskPublic:
    if not params.file and not params.storage and not params.website:
        raise BizException.create(
            ErrorCode.request_validation_error_detail,
            "neither file or storage or website is unset"
        )

    tenant_id = current_user.tenant_id
    knowledge_id = params.id

    entity = get_knowledge(session, knowledge_id, tenant_id)
    if not entity:
        raise BizException.create(ErrorCode.knowledge_not_found, knowledge_id)
    workspace_id = entity.workspace_id
    knowledge = KnowledgePublic.create(entity)

    model = get_embedding_model_from_config(
        session, knowledge.embedding_model_config, tenant_id)
    vector_store = get_vector_store_from_config(
        session, knowledge.vector_store_config, tenant_id)

    task_params = ImportTaskParams(
        tenant_id=tenant_id, workspace_id=workspace_id,
        knowledge=KnowledgePublic.create(entity),
        model=model, vector_store=vector_store,
    )
    # check params
    if params.file:
        file_ids = params.file.file_ids
        if not file_ids:
            raise BizException.create(
                ErrorCode.request_validation_error_detail,
                "file_ids is empty"
            )
        task_params.files = get_files(session, file_ids)
        missing_file_ids = [file_id for file_id in file_ids
                            if file_id not in task_params.files]
        if missing_file_ids:
            raise BizException.create(
                ErrorCode.file_not_found, missing_file_ids
            )
    elif params.storage:
        task_params.storage_files = get_storage_files(params.storage.file_path)
    else:
        task_params.page_urls = params.website.page_urls

    # import task
    return send_knowledge_import_task(task_params)
