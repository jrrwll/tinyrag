from sqlmodel import Session

from app.common.error_code import BizException, ErrorCode
from app.core.model.api import ModelCreate, ModelPublic, ModelTestRun, \
    ModelTestRunPublic, \
    ModelUpdate, ModelUpdateEnablePublic, SetupDefaultModel
from app.core.model.enums import ModelType, builtin_models
from app.core.model.llm.base import get_llm_provider
from app.entities.dao.model import get_default_model, get_default_models, \
    get_model, get_model_required
from app.entities.model import TenantDefaultModel
from app.entities.user import User
from app.util.api import IdResult


def create_model(session: Session, params: ModelCreate, current_user: User) -> IdResult:
    entity = params.to_entity()
    entity.tenant_id = current_user.tenant_id

    session.add(entity)
    session.commit()
    session.refresh(entity)
    return IdResult(id=entity.id)


def update_model(session: Session, params: ModelUpdate, current_user: User):
    entity = get_model(session, params.id, current_user.tenant_id)
    if not entity:
        raise BizException.create(ErrorCode.model_not_found, params.id)

    params.update_entity(entity)

    session.add(entity)
    session.commit()


def update_model_enable(
        session: Session, model_id: int, current_user: User
) -> ModelUpdateEnablePublic:
    entity = get_model(session, model_id, current_user.tenant_id)
    if not entity:
        raise BizException.create(ErrorCode.model_not_found, model_id)

    entity.enable = not entity.enable
    session.add(entity)
    session.commit()
    session.refresh(entity)

    return ModelUpdateEnablePublic(
        id=model_id, enable=entity.enable)


def delete_model(session: Session, model_id: int, current_user: User):
    default_models = get_default_models(current_user.tenant_id)
    default_model_ids = [i.model_id for i in default_models.values()
                         if not i.is_builtin()]
    if model_id in default_model_ids:
        raise BizException.create(ErrorCode.model_is_set_in_default)
    # TODO


def test_run_model(
        session: Session, params: ModelTestRun, current_user: User
) -> ModelTestRunPublic:
    entity = get_model_required(params.id, current_user.tenant_id, session)
    if not entity:
        raise BizException.create(ErrorCode.model_not_found, params.id)
    if entity.type != ModelType.LLM:
        raise BizException.create(
            ErrorCode.need_specific_type_model,
            ModelType.LLM.name, entity.type.name)

    model = ModelPublic.create(entity)
    provider = get_llm_provider(model)
    result = provider.test_run(params.prompt)
    return ModelTestRunPublic(result=result)


def find_default_model(
        session: Session, model_type: ModelType, current_user: User
) -> ModelPublic | None:
    default_model = get_default_model(
        session, model_type, current_user.tenant_id)
    if not default_model:
        return None

    if default_model.model_name:
        return ModelPublic.from_builtin(model_type, default_model.model_name)

    elif default_model.model_id:
        model_id = default_model.model_id
        model_entity = get_model(session, model_id, current_user.tenant_id)
        if not model_entity:
            raise BizException.create(ErrorCode.model_not_found, model_id)
        return ModelPublic.create(model_entity)


def set_or_unset_default_model(
        session: Session, params: SetupDefaultModel, current_user: User
):
    model_type, model_id, model_name = params.model_type, params.model_id, params.model_name

    entity = get_default_model(session, model_type, current_user.tenant_id)

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
            model_type=model_type,
            tenant_id=current_user.tenant_id,
        )

    if model_name:
        if model_name not in builtin_models.get(model_type, []):
            raise BizException.create(
                ErrorCode.request_validation_error_detail,
                f"model `{model_name}` is unsupported")

        entity.model_id = None
        entity.model_name = model_name
    else:
        model_entity = get_model(session, model_id, current_user.tenant_id)
        if not model_entity or model_entity.type != model_type:
            raise BizException.create(ErrorCode.model_not_found, model_id)

        entity.model_id = model_id
        entity.model_name = None

    session.add(entity)
    session.commit()
