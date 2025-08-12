# ruff: noqa: E712

from sqlmodel import Session, func, select

from app.core.model.enums import ModelType
from app.entities.model import Model, TenantDefaultModel


def page_and_count_models(
        session: Session, page_no: int, page_size: int, tenant_id: int
) -> tuple[list[dict], int]:
    conditions = [
        Model.tenant_id == tenant_id,
        Model.deleted == False,
    ]

    count_statement = (
        select(func.count()).select_from(Model).where(*conditions)
    )
    count = session.exec(count_statement).one()

    offset = (page_no - 1) * page_size
    limit = page_size

    page_statement = (
        select( # type: ignore[call-overload]
            Model.id,
            Model.created_at,
            Model.updated_at,
            Model.name,
            Model.type,
            Model.model_name,
            Model.provider_name,
            Model.enable,
        )
        .select_from(Model)
        .where(*conditions)
        .offset(offset)
        .limit(limit)
    )
    entities = session.exec(page_statement).mappings().all()
    return [dict(i) for i in entities], count


def get_model(session: Session, id: int, tenant_id: int) -> Model | None:
    conditions = [
        Model.id == id,
        Model.tenant_id == tenant_id,
    ]
    stmt = select(Model).where(*conditions)
    return session.exec(stmt).first()


def get_tenant_default_model(session: Session, model_type: ModelType, workspace_id: int | None, tenant_id: int
) -> TenantDefaultModel | None:
    conditions = [
        TenantDefaultModel.model_type == model_type,
        TenantDefaultModel.tenant_id == tenant_id,
    ]
    if workspace_id:
        conditions.append(TenantDefaultModel.workspace_id == workspace_id)

    stmt = select(TenantDefaultModel).where(*conditions)
    return session.exec(stmt).first()


def is_set_in_default_model(session: Session, model_id: int, tenant_id: int) -> bool:
    stmt = select(TenantDefaultModel).where(
        TenantDefaultModel.tenant_id == tenant_id,
        TenantDefaultModel.model_id == model_id
    ).limit(1)
    return session.exec(stmt).first() is not None
