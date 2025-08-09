from sqlmodel import Session

from app.common.error_code import BizException, ErrorCode
from app.core.meta.provider import ProviderMetaService
from app.core.model.api import ModelCreate, ModelPublic, ModelTestRun, \
    ModelTestRunPublic, \
    ModelUpdate, ModelUpdateConfig, SetupDefaultModel
from app.core.model.builtin_models import is_valid_model_name
from app.core.model.enums import ModelType
from app.core.model.feature import compute_model_feature
from app.core.model.llm.base import get_llm_provider
from app.entities.dao.model import get_model, get_tenant_default_model, \
    is_set_in_default_model
from app.entities.model import TenantDefaultModel
from app.entities.user import User
from app.util.api import IdResult


def create_model(session: Session, params: ModelCreate,
        current_user: User) -> IdResult:
    # validate config
    ProviderMetaService.from_model(params.type).validate_config_dict(
        params.provider_name, params.config)

    entity = params.to_entity()
    entity.tenant_id = current_user.tenant_id

    feature_config = compute_model_feature(entity)
    entity.feature_config = feature_config.model_dump_json()

    session.add(entity)
    session.commit()
    session.refresh(entity)
    return IdResult(id=entity.id)


def update_model_config(session: Session, params: ModelUpdateConfig,
        current_user: User):
    tenant_id = current_user.tenant_id
    entity = get_model(session, params.id, tenant_id)
    if not entity:
        raise BizException.create(ErrorCode.model_not_found)

    # validate config
    ProviderMetaService.from_model(entity.type).validate_config_dict(
        entity.provider_name, params.config)

    params.update_entity(entity)

    session.add(entity)
    session.commit()


def update_model(session: Session, params: ModelUpdate, current_user: User):
    tenant_id = current_user.tenant_id
    entity = get_model(session, params.id, tenant_id)
    if not entity:
        raise BizException.create(ErrorCode.model_not_found)

    params.update_entity(entity)

    session.add(entity)
    session.commit()


def delete_model(session: Session, model_id: int, current_user: User):
    tenant_id = current_user.tenant_id
    entity = get_model(session, model_id, tenant_id)
    if not entity:
        raise BizException.create(ErrorCode.model_not_found)

    if is_set_in_default_model(session, model_id, tenant_id):
        raise BizException.create(ErrorCode.model_is_set_in_default)

    # TODO


def test_run_model(
        session: Session, params: ModelTestRun, current_user: User
) -> ModelTestRunPublic:
    entity = get_model(session, params.id, current_user.tenant_id)
    if not entity:
        raise BizException.create(ErrorCode.model_not_found)
    if entity.type != ModelType.LLM:
        raise BizException.create(
            ErrorCode.model_not_llm, model_type=entity.type.name)

    model = ModelPublic.create(entity)
    provider = get_llm_provider(model)
    result = provider.test_run(params.prompt)
    return ModelTestRunPublic(result=result)


def find_default_model(
        session: Session, model_type: ModelType, workspace_id: int | None,
        current_user: User
) -> ModelPublic | None:
    entity = get_tenant_default_model(
        session, model_type, workspace_id, current_user.tenant_id)
    if not entity or entity.is_unset():
        if workspace_id:
            # tenant default
            entity = get_tenant_default_model(
                session, model_type, None, current_user.tenant_id)
        if not entity or entity.is_unset():
            return None

    if entity.model_name:
        return ModelPublic.from_builtin(model_type, entity.model_name)

    elif entity.model_id:
        model_id = entity.model_id
        model_entity = get_model(session, model_id, current_user.tenant_id)
        if not model_entity:
            raise BizException.create(ErrorCode.model_id_not_found, id=model_id)
        return ModelPublic.create(model_entity)
    else:
        return None


def set_or_unset_default_model(
        session: Session, params: SetupDefaultModel, current_user: User
):
    workspace_id, model_type = params.workspace_id, params.model_type
    model_id, model_name = params.model_id, params.model_name

    entity = get_tenant_default_model(session, model_type, workspace_id,
                                      current_user.tenant_id)

    # unset case
    if not model_id and not model_name:
        if not entity or entity.is_unset():
            return

        entity.model_id = None
        entity.model_name = None
        session.add(entity)
        session.commit()
        return

    # set case
    if not entity:
        entity = TenantDefaultModel(
            tenant_id=current_user.tenant_id,
            workspace_id=workspace_id,
            model_type=model_type,
        )

    if model_name:
        if not is_valid_model_name(model_type, model_name):
            raise BizException.create(ErrorCode.model_name_not_supported,
                                      model_name=model_name)

        entity.model_id = None
        entity.model_name = model_name
    else:
        model_entity = get_model(session, model_id, current_user.tenant_id)
        if not model_entity or model_entity.type != model_type:
            raise BizException.create(ErrorCode.model_not_found)

        entity.model_id = model_id
        entity.model_name = None

    session.add(entity)
    session.commit()
