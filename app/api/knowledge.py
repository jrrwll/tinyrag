from typing import Any

from app.api import CustomAPIRouter
from app.common.deps import CurrentUser, LogDep, SessionDep
from app.common.error_code import BizException, ErrorCode
from app.config import settings
from app.core.knowledge.api import DocumentPreviewChunk, \
    DocumentPreviewChunkPublic, \
    KnowledgeChat, KnowledgeChatPublic, KnowledgeCreate, KnowledgeImport, \
    KnowledgePublic, KnowledgeStartConversation, KnowledgeStreamChatPublic, \
    KnowledgeUpdate, KnowledgeUpdateConfig, SimpleKnowledgePublic
from app.core.knowledge.service.base import create_knowledge, update_knowledge, \
    update_knowledge_config
from app.core.knowledge.service.chat import chat_knowledge
from app.core.knowledge.service.conversation import start_conversation
from app.core.knowledge.service.import_task import import_documents
from app.core.knowledge.service.preview_file_chunk import preview_file_chunk
from app.core.knowledge.service.stream_chat import stream_chat_knowledge
from app.core.task.api import AsyncTaskPublic
from app.entities.dao.knowledge import page_and_count_knowledges
from app.entities.knowledge import Knowledge
from app.util.api import ApiResult, IdResult, PageResult

router = CustomAPIRouter(prefix="/knowledge", tags=["knowledge"])


@router.get("/list",
            response_model=ApiResult[PageResult[SimpleKnowledgePublic]])
def _list(
        session: SessionDep,
        current_user: CurrentUser,
        workspace_id: int,
        page_no: int = settings.page_no_query,
        page_size: int = settings.page_size_query,
        enable: bool | None = None,
) -> Any:
    entities, count = page_and_count_knowledges(
        session, page_no, page_size, workspace_id, enable, current_user.tenant_id)
    res = PageResult[SimpleKnowledgePublic](
        page_no=page_no,
        page_size=page_size,
        total=count,
        items=[SimpleKnowledgePublic(**entity) for entity in entities],
    )
    return ApiResult.create(res)


@router.get("", response_model=ApiResult[KnowledgePublic])
def _get(session: SessionDep, id: str) -> Any:
    entity = session.get(Knowledge, id)
    if not entity:
        raise BizException.create(ErrorCode.knowledge_not_found)

    return ApiResult.create(KnowledgePublic.create(entity))


@router.post("/preview-chunk",
             response_model=ApiResult[DocumentPreviewChunkPublic],
             dependencies=[LogDep])
def _preview_chunk(params: DocumentPreviewChunk, current_user: CurrentUser) -> Any:
    res = preview_file_chunk(params, current_user.tenant_id)
    return ApiResult.create(res)


@router.post("", response_model=ApiResult[IdResult],
             dependencies=[LogDep])
def _create(session: SessionDep, params: KnowledgeCreate,
        current_user: CurrentUser) -> Any:
    res = create_knowledge(session, params, current_user)
    return ApiResult.create(res)


@router.put("", response_model=ApiResult[Any], dependencies=[LogDep])
def _update(session: SessionDep, params: KnowledgeUpdate,
        current_user: CurrentUser) -> Any:
    update_knowledge(session, params, current_user)
    return ApiResult.create()


@router.post("/config", response_model=ApiResult[Any], dependencies=[LogDep])
def _update_config(session: SessionDep, params: KnowledgeUpdateConfig,
        current_user: CurrentUser) -> Any:
    update_knowledge_config(session, params, current_user)
    return ApiResult.create()


@router.post("/import", response_model=ApiResult[AsyncTaskPublic],
             dependencies=[LogDep])
def _import_document(session: SessionDep, params: KnowledgeImport,
        current_user: CurrentUser) -> Any:
    res = import_documents(session, params, current_user)
    return ApiResult.create(res)


@router.post("/conversation", response_model=ApiResult[IdResult])
def _conversation(session: SessionDep, params: KnowledgeStartConversation,
        current_user: CurrentUser):
    res = start_conversation(session, params, current_user)
    return ApiResult.create(res)


@router.post("/chat", response_model=ApiResult[KnowledgeChatPublic])
def chat(session: SessionDep, params: KnowledgeChat,
        current_user: CurrentUser):
    res = chat_knowledge(session, params, current_user)
    return ApiResult.create(res)


@router.post("/stream-chat",
             response_model=ApiResult[KnowledgeStreamChatPublic])
def stream_chat(session: SessionDep, params: KnowledgeChat,
        current_user: CurrentUser):
    res = stream_chat_knowledge(session, params, current_user)
    return ApiResult.create(res)
