# ruff: noqa: E712
from sqlmodel import Session, and_, func, select

from app.common.deps import open_session
from app.entities.knowledge import Knowledge, KnowledgeConversation, \
    KnowledgeDocument, \
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


def get_knowledges(session: Session, ids: list[int], tenant_id: int) -> list[Knowledge]:
    stmt = select(Knowledge).where(
        Knowledge.id.in_(ids),
        Knowledge.tenant_id == tenant_id,
        Knowledge.deleted == False
    )
    return session.exec(stmt).all()


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


def page_and_count_documents(
        session: Session, page_no: int, page_size: int,
        knowledge_id: int, tenant_id: int
) -> tuple[list[KnowledgeDocument], int]:  # type: ignore[type-arg]
    conditions = [
        KnowledgeDocument.tenant_id == tenant_id,
        KnowledgeDocument.knowledge_id == knowledge_id,
    ]

    count_statement = (
        select(func.count()).select_from(KnowledgeDocument).where(*conditions)
    )
    count = session.exec(count_statement).one()

    offset = (page_no - 1) * page_size
    limit = page_size

    page_statement = (
        select(KnowledgeDocument)
        .where(*conditions)
        .order_by(KnowledgeDocument.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    entities = session.exec(page_statement).all()
    return entities, count


def get_knowledge_conversation(
        session: Session, id: str, tenant_id: int
) -> KnowledgeConversation | None:
    stmt = select(KnowledgeConversation).where(
        KnowledgeConversation.id == id,
        KnowledgeConversation.tenant_id == tenant_id,
        KnowledgeConversation.deleted == False
    )
    return session.exec(stmt).first()
