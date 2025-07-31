from sqlmodel import Session

from app.common.error_code import BizException, ErrorCode
from app.core.file.service.base import get_storage_files
from app.core.knowledge.api import KnowledgeImport, \
    KnowledgePublic
from app.core.task.api import AsyncTaskPublic
from app.entities.dao.file import get_files
from app.entities.knowledge import Knowledge
from app.entities.user import User
from app.tasks.knowledge_import import send_knowledge_import_task


def import_documents(session: Session, params: KnowledgeImport, current_user: User) -> AsyncTaskPublic:
    if not params.file and not params.storage and not params.website:
        raise BizException.create(
            ErrorCode.request_validation_error_detail,
            "neither file or storage or website is unset"
        )

    knowledge_id = params.id
    entity = session.get(Knowledge, knowledge_id)
    if not entity:
        raise BizException.create(ErrorCode.knowledge_not_found, knowledge_id)

    files = {}
    storage_files = []
    # check params
    if params.file:
        file_ids = params.file.file_ids
        if not file_ids:
            raise BizException.create(
                ErrorCode.request_validation_error_detail,
                "file_ids is empty"
            )
        files = get_files(session, file_ids)
        missing_file_ids = [file_id for file_id in file_ids
                            if file_id not in files]
        if missing_file_ids:
            raise BizException.create(
                ErrorCode.file_not_found, missing_file_ids
            )
    elif params.storage:
        storage_files = get_storage_files(params.storage.file_path)

    # import task
    knowledge = KnowledgePublic.create(entity)
    return send_knowledge_import_task(params, knowledge, files, storage_files)
