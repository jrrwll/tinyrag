# ruff: noqa: E712
from sqlmodel import Session, and_, func, select

from app.common.deps import open_session
from app.entities.knowledge import Knowledge, KnowledgeDocument, \
    KnowledgeDocumentChunk


def page_and_count_knowledges(
        session: Session, page_no: int, page_size: int,
        workspace_id: int, enable: bool | None, tenant_id: int
) -> tuple[list[dict], int]:  # type: ignore[type-arg]
    conditions = [
        Knowledge.tenant_id == tenant_id,
        Knowledge.workspace_id == workspace_id,
        Knowledge.deleted == False
    ]
    if enable:
        conditions.append(Knowledge.enable == enable)

    count_statement = (
        select(func.count()).select_from(Knowledge).where(and_(*conditions))
    )
    count = session.exec(count_statement).one()

    offset = (page_no - 1) * page_size
    limit = page_size

    page_statement = (
        select(  # type: ignore[call-overload]
            Knowledge.id,
            Knowledge.name,
            Knowledge.description,
            Knowledge.enable,
            Knowledge.created_at,
            Knowledge.updated_at,
        )
        .select_from(Knowledge)
        .where(and_(*conditions))
        .offset(offset)
        .limit(limit)
    )
    models = session.exec(page_statement).mappings().all()
    return [dict(i) for i in models], count


def get_knowledge(session: Session, id: int, tenant_id: int) -> Knowledge | None:
    stmt = select(Knowledge).where(
        Knowledge.id == id,
        Knowledge.tenant_id == tenant_id,
        Knowledge.deleted == False
    )
    return session.exec(stmt).first()

def save_knowledge_document(entity: KnowledgeDocument) -> KnowledgeDocument:
    with open_session() as session:
        session.add(entity)
        session.commit()
        session.refresh(entity)
    return entity


def save_knowledge_document_chucks(
        entities: list[KnowledgeDocumentChunk]) -> None:
    with open_session() as session:
        session.add_all(entities)
        session.commit()
