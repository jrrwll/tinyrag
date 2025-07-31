from app.common.error_code import BizException, ErrorCode
from app.core.knowledge.api import KnowledgeCreate, KnowledgeUpdate
from app.entities.knowledge import Knowledge
from app.entities.user import User
from app.util.api import IdResult
from sqlmodel import Session


def create_knowledge(session: Session, params: KnowledgeCreate, current_user: User) -> IdResult:
    entity = params.to_entity()
    entity.tenant_id = current_user.tenant_id

    session.add(entity)
    session.commit()
    session.refresh(entity)
    return IdResult(id=entity.id)


def update_knowledge(session: Session, params: KnowledgeUpdate, current_user: User):
    id = params.id
    entity = session.get(Knowledge, id)
    if not entity:
        raise BizException.create(ErrorCode.knowledge_not_found, id)

    params.update_entity(entity)

    session.add(entity)
    session.commit()