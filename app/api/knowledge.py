from typing import Any

from mypy.binder import CurrentType

from app.api import CustomAPIRouter
from app.common.deps import CurrentUser, SessionDep
from app.common.error_code import BizException, ErrorCode
from app.common.log import LogDep
from app.config import settings
from app.core.file.service.base import get_storage_files
from app.core.knowledge.api import DocumentPreviewChunk, \
    DocumentPreviewChunkPublic, \
    KnowledgeChat, KnowledgeChatPublic, KnowledgeCreate, KnowledgeImport, \
    KnowledgePublic, KnowledgeStreamChatPublic, KnowledgeUpdate, \
    SimpleKnowledgePublic
from app.core.knowledge.service.chat import chat_knowledge
from app.core.knowledge.service.preview_file_chunk import preview_file_chunk
from app.core.knowledge.service.stream_chat import stream_chat_knowledge
from app.core.task.api import AsyncTaskPublic
from app.entities.dao.file import get_files
from app.entities.dao.knowledge import page_and_count_knowledges
from app.entities.knowledge import Knowledge, KnowledgeConversation
from app.tasks.knowledge_import import send_knowledge_import_task
from app.util.api import ApiResult, IdResult, PageResult

router = CustomAPIRouter(prefix="/knowledge", tags=["knowledge"])


@router.get("/list", response_model=ApiResult[PageResult[SimpleKnowledgePublic]])
def list(
        session: SessionDep,
        workspace_id: int,
        page_no: int = settings.page_no_query,
        page_size: int = settings.page_size_query,
        enable: bool | None = None,
) -> Any:
    entities, count = page_and_count_knowledges(
        session, page_no, page_size, workspace_id, enable)
    res = PageResult[SimpleKnowledgePublic](
        page_no=page_no,
        page_size=page_size,
        total=count,
        items=[SimpleKnowledgePublic(**entity) for entity in entities],
    )
    return ApiResult.create(res)


@router.get("", response_model=ApiResult[KnowledgePublic])
def get(session: SessionDep, id: str) -> Any:
    entity = session.get(Knowledge, id)
    if not entity:
        raise BizException.create(ErrorCode.knowledge_not_found, id)

    return ApiResult.create(KnowledgePublic.create(entity))


@router.post("/preview-chunk", response_model=ApiResult[DocumentPreviewChunkPublic],
             dependencies=[LogDep])
def preview_chunk(params: DocumentPreviewChunk) -> Any:
    return ApiResult.create(preview_file_chunk(params))


@router.post("", response_model=ApiResult[KnowledgePublic], dependencies=[LogDep])
def create(session: SessionDep, params: KnowledgeCreate,
        current_user: CurrentUser) -> Any:
    entity = params.to_entity()
    entity.tenant_id = current_user.tenant_id

    session.add(entity)
    session.commit()
    session.refresh(entity)
    return ApiResult.create(KnowledgePublic.create(entity))


@router.put("", response_model=ApiResult[Any], dependencies=[LogDep])
def update(session: SessionDep, params: KnowledgeUpdate) -> Any:
    id = params.id
    entity = session.get(Knowledge, id)
    if not entity:
        raise BizException.create(ErrorCode.knowledge_not_found, id)

    params.update_entity(entity)

    session.add(entity)
    session.commit()

    return ApiResult.create()


@router.post("/import", response_model=ApiResult[AsyncTaskPublic],
             dependencies=[LogDep])
def import_document(session: SessionDep, params: KnowledgeImport) -> Any:
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
    task = send_knowledge_import_task(params, knowledge, files, storage_files)
    return ApiResult.create(task)


@router.post("/conversation", response_model=ApiResult[IdResult])
def start_conversation(session: SessionDep, id: str):
    knowledge_entity = session.get(Knowledge, id)
    if not knowledge_entity:
        raise BizException.create(ErrorCode.knowledge_not_found, id)

    entity = KnowledgeConversation(knowledge_id=id)
    session.add(entity)
    session.commit()
    session.refresh(entity)
    return ApiResult.create(IdResult(id=entity.id))


@router.post("/chat", response_model=ApiResult[KnowledgeChatPublic])
def chat(session: SessionDep, params: KnowledgeChat):
    conversation_id = params.conversation_id
    entity = session.get(KnowledgeConversation, conversation_id)
    if not entity:
        raise BizException.create(ErrorCode.knowledge_conversation_not_found, id)

    knowledge_id = entity.knowledge_id
    knowledge_entity = session.get(Knowledge, knowledge_id)
    if not knowledge_entity:
        raise BizException.create(ErrorCode.knowledge_not_found, id)

    res = chat_knowledge(entity, knowledge_entity)
    return ApiResult.create(res)


@router.post("/stream-chat", response_model=ApiResult[KnowledgeStreamChatPublic])
def stream_chat(session: SessionDep, params: KnowledgeChat):
    conversation_id = params.conversation_id
    entity = session.get(KnowledgeConversation, conversation_id)
    if not entity:
        raise BizException.create(ErrorCode.knowledge_conversation_not_found, id)

    knowledge_id = entity.knowledge_id
    knowledge_entity = session.get(Knowledge, knowledge_id)
    if not knowledge_entity:
        raise BizException.create(ErrorCode.knowledge_not_found, id)

    res = stream_chat_knowledge(entity, knowledge_entity)
    return ApiResult.create(res)
