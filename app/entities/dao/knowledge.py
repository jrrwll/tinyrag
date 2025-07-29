# ruff: noqa: E712
from sqlmodel import and_, func, select

from app.common.deps import SessionDep, open_session
from app.entities.knowledge import Knowledge, KnowledgeDocument, \
    KnowledgeDocumentChunk


def page_and_count_knowledges(
        session: SessionDep, page_no: int, page_size: int, enable: bool | None
) -> tuple[list[dict], int]:  # type: ignore[type-arg]
    conditions = [Knowledge.deleted == False]
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
