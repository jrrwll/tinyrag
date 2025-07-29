from typing import Any, Optional

from fastapi import Depends

from app.api import CustomAPIRouter
from app.common.deps import CurrentUser, SessionDep, \
    get_current_active_superuser
from app.common.error_code import BizException, ErrorCode
from app.config import settings
from app.core.model.api import (
    ModelCreate,
    ModelPublic,
    ModelTestRun,
    ModelTestRunPublic,
    ModelUpdate, ModelUpdateEnablePublic, SetupDefaultModel,
)
from app.core.model.enums import ModelType, builtin_models
from app.core.model.privoder.base import get_model_provider
from app.entities.dao.model import get_default_model, get_model, \
    page_and_count_models
from app.entities.model import TenantDefaultModel
from app.util.api import ApiResult, IdResult, PageResult

router = CustomAPIRouter(prefix="/model", tags=["model"])


@router.get("/list", response_model=ApiResult[PageResult[ModelPublic]])
def list(
        session: SessionDep,
        current_user: CurrentUser,
        page_no: int = settings.page_no_query,
        page_size: int = settings.page_size_query,
) -> Any:
    entities, count = page_and_count_models(
        session, page_no, page_size, current_user.tenant_id)
    res = PageResult[ModelPublic](
        page_no=page_no,
        page_size=page_size,
        total=count,
        items=[ModelPublic.create(entity) for entity in entities],
    )
    return ApiResult.create(res)


@router.get("", response_model=ApiResult[ModelPublic])
def get(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    entity = get_model(session, id, current_user.tenant_id)
    if not entity:
        raise BizException.create(ErrorCode.model_not_found, id)

    return ApiResult.create(ModelPublic.create(entity))


@router.post("", response_model=ApiResult[IdResult])
def create(session: SessionDep, current_user: CurrentUser,
        params: ModelCreate) -> Any:
    entity = params.to_entity()
    entity.tenant_id = current_user.tenant_id

    session.add(entity)
    session.commit()
    session.refresh(entity)

    return ApiResult.create(IdResult(id=entity.id))


@router.put("", response_model=ApiResult[Any])
def update(session: SessionDep, current_user: CurrentUser,
        params: ModelUpdate) -> Any:
    entity = get_model(session, params.id, current_user.tenant_id)
    if not entity:
        raise BizException.create(ErrorCode.model_not_found, params.id)

    params.update_entity(entity)

    session.add(entity)
    session.commit()

    return ApiResult.create()


@router.post("/update-enable",
             response_model=ApiResult[ModelUpdateEnablePublic])
def update_enable(session: SessionDep, current_user: CurrentUser,
        id: int) -> Any:
    entity = get_model(session, id, current_user.tenant_id)
    if not entity:
        raise BizException.create(ErrorCode.model_not_found, id)

    entity.enable = not entity.enable
    session.add(entity)
    session.commit()
    session.refresh(entity)

    return ApiResult.create(ModelUpdateEnablePublic(
        id=id, enable=entity.enable))


@router.delete("", response_model=ApiResult[Any])
def delete(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    entity = get_model(session, id, current_user.tenant_id)
    if not entity:
        raise BizException.create(ErrorCode.model_not_found, id)

    session.delete(entity)
    session.commit()
    return ApiResult.create()


@router.post("/test-run", response_model=ApiResult[ModelTestRunPublic])
def test_run(session: SessionDep, current_user: CurrentUser,
        params: ModelTestRun) -> Any:
    entity = get_model(session, params.id, current_user.tenant_id)
    if not entity:
        raise BizException.create(ErrorCode.model_not_found, params.id)

    model = ModelPublic.create(entity)
    provider = get_model_provider(model)
    result = provider.test_run(params.prompt)
    return ApiResult.create(ModelTestRunPublic(result=result))


@router.get("/default-model", response_model=ApiResult[Optional[ModelPublic]])
def default_model(session: SessionDep, current_user: CurrentUser,
        model_type: ModelType) -> Any:
    default_model = get_default_model(
        session, model_type, current_user.tenant_id)
    if not default_model:
        return ApiResult.create()

    res = None
    if default_model.model_name:
        res = ModelPublic.from_builtin(model_type, default_model.model_name)

    elif default_model.model_id:
        model_id = default_model.model_id
        model_entity = get_model(session, model_id, current_user.tenant_id)
        if not model_entity:
            raise BizException.create(ErrorCode.model_not_found, model_id)
        res = ModelPublic.create(model_entity)

    return ApiResult.create(res)


@router.post("/default-model", response_model=ApiResult[Any])
def set_or_unset_default_model(session: SessionDep, params: SetupDefaultModel,
        current_user = Depends(get_current_active_superuser)) -> Any:
    model_type, model_id, model_name = params.model_type, params.model_id, params.model_name

    entity = get_default_model(session, model_type, current_user.tenant_id)

    # unset case
    if not model_id and not model_name:
        if not entity or entity.is_unset():
            return ApiResult.create()

        entity.model_id = None
        entity.model_name = None
        session.add(entity)
        session.commit()
        session.refresh(entity)
        return ApiResult.create()

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
    return ApiResult.create()
