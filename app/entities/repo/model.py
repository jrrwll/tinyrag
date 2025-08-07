from sqlmodel import Session, or_, select

from app.common.error_code import BizException, ErrorCode
from app.core.knowledge.base import EmbeddingModelConfig
from app.core.model.api import ModelPublic
from app.core.model.enums import ModelType
from app.entities.dao.model import get_default_model, get_model
from app.entities.model import Model, TenantDefaultModel


def get_embedding_model_from_config(
        session: Session,
        embedding_model_config: EmbeddingModelConfig, tenant_id: int) -> ModelPublic:
    if embedding_model_config.model_name:
        return ModelPublic.from_builtin(ModelType.TextEmbedding, embedding_model_config.model_name)
    model_id = embedding_model_config.model_id
    model = get_model(session, model_id, tenant_id)
    if not model:
        raise BizException.create(ErrorCode.model_not_found, model_id)
    return ModelPublic.create(model)


def get_setup_model(
        session: Session, model_type: ModelType,
        workspace_id: int, tenant_id: int,
        required: bool = False) -> ModelPublic | None:
    entity = get_default_model(session, model_type, workspace_id, tenant_id)
    if not entity or entity.is_unset():
        entity = get_default_model(session, model_type, None, tenant_id)
    if not entity or entity.is_unset():
        if required:
            raise BizException.create(ErrorCode.model_not_set, model_type)
        else:
            return None

    if entity.model_name:
        return ModelPublic.from_builtin(model_type, entity.model_name)
    model_entity = get_model(session, entity.model_id, tenant_id)
    if not model_entity:
        if required:
            raise BizException.create(ErrorCode.model_not_found, entity.model_id)
        else:
            return None
    return ModelPublic.create(model_entity)


def get_setup_models(
        session: Session, workspace_id: int, tenant_id: int
) -> dict[ModelType, ModelPublic]:
    conditions = [
        TenantDefaultModel.tenant_id == tenant_id,
        or_(TenantDefaultModel.workspace_id == workspace_id,
            TenantDefaultModel.workspace_id == 0)
    ]

    stmt = select(TenantDefaultModel).where(*conditions)
    entities = session.exec(stmt).all()

    entity_dict = {m.model_type: m for m in entities if m.workspace_id != 0}
    for entity in entities:
        if entity.workspace_id == 0 and entity.model_type not in entity_dict:
            entity_dict[entity.model_type] = entity

    builtin_models = [
        ModelPublic.from_builtin(model_type, m.model_name)
        for model_type, m in entity_dict.items()
        if m.model_name
    ]

    custom_models = []
    model_ids = [m.model_id for m in entity_dict.values() if m.model_id]
    if model_ids:
        select_in_statement = select(Model).where(
            Model.id.in_(model_ids),
            Model.tenant_id == tenant_id,
            Model.deleted == False
        )
        models = session.exec(select_in_statement).all()
        custom_models = [ModelPublic.create(model) for model in models]

    return {model.type: model for model in builtin_models + custom_models}
