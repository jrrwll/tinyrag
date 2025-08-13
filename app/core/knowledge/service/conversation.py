from uuid import uuid4

from sqlmodel import Session

from app.common.error_code import BizException, ErrorCode
from app.core.knowledge.api import KnowledgeStartConversation
from app.entities.knowledge import Knowledge, KnowledgeConversation
from app.entities.user import User
from app.util.api import IdResult


def start_conversation(session: Session, params: KnowledgeStartConversation, current_user: User) -> IdResult:
    knowledge_id = params.knowledge_id

    knowledge_entity = session.get(Knowledge, knowledge_id)
    if not knowledge_entity:
        raise BizException.create(ErrorCode.knowledge_not_found)

    id = str(uuid4())
    entity = KnowledgeConversation(
        id=id,
        knowledge_id=knowledge_id,
        tenant_id=current_user.tenant_id,
        workspace_id=knowledge_entity.workspace_id
    )

    session.add(entity)
    session.commit()

    return IdResult(id=id)
