from sqlmodel import Session

from app.common.error_code import BizException, ErrorCode
from app.core.knowledge.api import KnowledgeChat, KnowledgeStreamChatPublic
from app.entities.knowledge import Knowledge, KnowledgeConversation
from app.entities.user import User


def stream_chat_knowledge(
        session: Session, params: KnowledgeChat, current_user: User
) -> KnowledgeStreamChatPublic:
    conversation_id = params.conversation_id
    entity = session.get(KnowledgeConversation, conversation_id)
    if not entity:
        raise BizException.create(ErrorCode.knowledge_conversation_not_found, id)

    knowledge_id = entity.knowledge_id
    knowledge_entity = session.get(Knowledge, knowledge_id)
    if not knowledge_entity:
        raise BizException.create(ErrorCode.knowledge_not_found, id)

    raise NotImplementedError()
