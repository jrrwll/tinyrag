# ruff: noqa: E712
from typing import Sequence

from sqlmodel import Session, func, select

from app.common.deps import open_session
from app.common.error_code import BizException, ErrorCode
from app.core.model.api import ModelPublic
from app.core.model.enums import ModelType
from app.entities.model import Model, TenantDefaultModel


def page_and_count_models(
        session: Session, page_no: int, page_size: int, tenant_id: int
) -> tuple[Sequence[Model], int]:
    conditions = [Model.tenant_id == tenant_id, Model.deleted == False]

    count_statement = (
        select(func.count()).select_from(Model).where(*conditions)
    )
    count = session.exec(count_statement).one()

    offset = (page_no - 1) * page_size
    limit = page_size

    page_statement = (
        select(Model)
        .where(*conditions)
        .offset(offset)
        .limit(limit)
    )
    entities = session.exec(page_statement).all()
    return entities, count


def get_model_required(
        id: int, tenant_id: int | None = None,
        session: Session | None = None) -> Model:
    conditions = [Model.id == id, Model.deleted == False]
    if tenant_id is not None:
        conditions.append(Model.tenant_id == tenant_id)
    stmt = select(Model).where(*conditions)

    entity: Model | None = None
    if session:
        entity = session.exec(stmt).first()
    else:
        with open_session() as session:
            entity = session.exec(stmt).first()
    if not entity:
        raise BizException.create(ErrorCode.model_not_found, id)
    return entity


def get_model(session: Session, id: int, tenant_id: int) -> Model | None:
    stmt = select(Model).where(
        Model.id == id, Model.tenant_id == tenant_id
    )
    return session.exec(stmt).first()


def get_default_model(session: Session, model_type: ModelType, workspace_id: int | None, tenant_id: int
) -> TenantDefaultModel | None:
    conditions = [
        TenantDefaultModel.model_type == model_type,
        TenantDefaultModel.tenant_id == tenant_id,
    ]
    if workspace_id:
        conditions.append(TenantDefaultModel.workspace_id == workspace_id)

    stmt = select(TenantDefaultModel).where(*conditions)
    return session.exec(stmt).first()


def get_default_models(tenant_id: int) -> dict[ModelType, ModelPublic]:
    with open_session() as session:
        stmt = select(TenantDefaultModel).where(
            TenantDefaultModel.tenant_id == tenant_id)
        default_models = session.exec(stmt).all()

        model_type_names = {
            default_model.model_type: default_model.model_name
            for default_model in default_models
            if default_model.model_name
        }
        system_models = [
            ModelPublic.from_builtin(model_type, model_name)
            for model_type, model_name in model_type_names.items()
        ]

        custom_models = []
        model_ids = [default_model.model_id
                     for default_model in default_models
                     if default_model.model_id]
        if model_ids:
            select_in_statement = select(Model).where(
                Model.id.in_(model_ids),
                Model.deleted == False
            )
            models = session.exec(select_in_statement).all()
            custom_models = [ModelPublic.create(model) for model in models]

        return {model.type: model for model in system_models + custom_models}
