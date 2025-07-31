from typing import Sequence

from sqlmodel import Session, func, select

from app.entities.vector_store import TenantDefaultVectorStore, VectorStore


def page_and_count_vector_stores(
        session: Session, page_no: int, page_size: int, tenant_id: int
) -> tuple[Sequence[VectorStore], int]:
    conditions = [VectorStore.tenant_id == tenant_id]

    count_statement = (
        select(func.count()).select_from(VectorStore).where(*conditions)
    )
    count = session.exec(count_statement).one()

    offset = (page_no - 1) * page_size
    limit = page_size

    page_statement = (
        select(VectorStore)
        .where(*conditions)
        .offset(offset)
        .limit(limit)
    )
    entities = session.exec(page_statement).all()
    return entities, count


def get_vector_store(
        session: Session, id: int, tenant_id: int
) -> VectorStore | None:
    stmt = select(VectorStore).where(
        VectorStore.id == id, VectorStore.tenant_id == tenant_id
    )
    return session.exec(stmt).first()


def get_default_vector_store(
        session: Session, workspace_id: int | None, tenant_id: int
) -> TenantDefaultVectorStore | None:
    conditions = [
        TenantDefaultVectorStore.tenant_id == tenant_id
    ]
    if workspace_id:
        conditions.append(TenantDefaultVectorStore.workspace_id == workspace_id)

    stmt = select(TenantDefaultVectorStore).where(*conditions)
    return session.exec(stmt).first()
