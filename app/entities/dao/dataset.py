# ruff: noqa: E712
from sqlmodel import and_, func, select

from app.common.db import open_session
from app.common.db import SessionDep
from app.entities.dataset import Dataset, Document, DocumentChunk


def page_and_count_datasets(
        session: SessionDep, page_no: int, page_size: int, enable: bool | None
) -> tuple[list[dict], int]:  # type: ignore[type-arg]
    conditions = [Dataset.deleted == False]
    if enable:
        conditions.append(Dataset.enable == enable)

    count_statement = (
        select(func.count()).select_from(Dataset).where(and_(*conditions))
    )
    count = session.exec(count_statement).one()

    offset = (page_no - 1) * page_size
    limit = page_size

    page_statement = (
        select(  # type: ignore[call-overload]
            Dataset.id,
            Dataset.name,
            Dataset.description,
            Dataset.enable,
            Dataset.created_at,
            Dataset.updated_at,
        )
        .select_from(Dataset)
        .where(and_(*conditions))
        .offset(offset)
        .limit(limit)
    )
    models = session.exec(page_statement).mappings().all()
    return [dict(i) for i in models], count


def save_document(entity: Document) -> Document:
    with open_session() as session:
        session.add(entity)
        session.commit()
        session.refresh(entity)
    return entity


def save_document_chucks(entities: list[DocumentChunk]) -> None:
    with open_session() as session:
        session.add_all(entities)
        session.commit()
