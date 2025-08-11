from sqlmodel import Session, func, select

from app.entities.storage import Storage, TenantDefaultStorage


def page_and_count_storages(
        session: Session, page_no: int, page_size: int, tenant_id: int
) -> tuple[list[dict], int]:
    conditions = [
        Storage.tenant_id == tenant_id,
        Storage.deleted == False,
    ]

    count_statement = (
        select(func.count()).select_from(Storage).where(*conditions)
    )
    count = session.exec(count_statement).one()

    offset = (page_no - 1) * page_size
    limit = page_size

    page_statement = (
        select(  # type: ignore[call-overload]
            Storage.id,
            Storage.created_at,
            Storage.updated_at,
            Storage.name,
            Storage.type,
        )
        .select_from(Storage)
        .where(*conditions)
        .offset(offset)
        .limit(limit)
    )
    entities = session.exec(page_statement).mappings().all()
    return [dict(i) for i in entities], count


def get_storage(
        session: Session, id: int, tenant_id: int
) -> Storage | None:
    conditions = [
        Storage.id == id,
        Storage.tenant_id == tenant_id,
    ]
    stmt = select(Storage).where(*conditions)
    return session.exec(stmt).first()


def get_tenant_default_storage(
        session: Session, workspace_id: int | None, tenant_id: int
) -> TenantDefaultStorage | None:
    conditions = [
        TenantDefaultStorage.tenant_id == tenant_id
    ]
    if workspace_id:
        conditions.append(TenantDefaultStorage.workspace_id == workspace_id)

    stmt = select(TenantDefaultStorage).where(*conditions)
    return session.exec(stmt).first()
