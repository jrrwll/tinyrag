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
    ModelUpdate, ModelUpdateConfig, SetupDefaultModel,
)
from app.core.model.enums import ModelType
from app.core.model.service import create_model, delete_model, \
    find_default_model, set_or_unset_default_model, test_run_model, \
    update_model, update_model_config
from app.entities.dao.model import get_model, \
    page_and_count_models
from app.entities.user import User
from app.util.api import ApiResult, IdResult, PageResult

router = CustomAPIRouter(prefix="/model", tags=["model"])


@router.get("/list", response_model=ApiResult[PageResult[ModelPublic]])
def _list(
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


@router.get("", response_model=ApiResult[ModelPublic],
            response_model_exclude={"data": {"feature_config"}})
def _get(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    entity = get_model(session, id, current_user.tenant_id)
    if not entity:
        raise BizException.create(ErrorCode.model_not_found)

    return ApiResult.create(ModelPublic.create(entity))


@router.post("", response_model=ApiResult[IdResult])
def _create(session: SessionDep, current_user: CurrentUser,
        params: ModelCreate) -> Any:
    res = create_model(session, params, current_user)
    return ApiResult.create(res)


@router.put("/config",
            response_model=ApiResult[Any])
def _update_config(session: SessionDep, current_user: CurrentUser,
        params: ModelUpdateConfig) -> Any:
    res = update_model_config(session, params, current_user)
    return ApiResult.create(res)


@router.put("", response_model=ApiResult[Any])
def _update(session: SessionDep, current_user: CurrentUser,
        params: ModelUpdate) -> Any:
    update_model(session, params, current_user)
    return ApiResult.create()


@router.delete("", response_model=ApiResult[Any])
def _delete(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    delete_model(session, id, current_user)
    return ApiResult.create()


@router.post("/test-run", response_model=ApiResult[ModelTestRunPublic])
def _test_run(session: SessionDep, current_user: CurrentUser,
        params: ModelTestRun) -> Any:
    res = test_run_model(session, params, current_user)
    return ApiResult.create(res)


@router.get("/default", response_model=ApiResult[Optional[ModelPublic]])
def _get_default(session: SessionDep, current_user: CurrentUser,
        model_type: ModelType, workspace_id: int | None = None) -> Any:
    res = find_default_model(session, model_type, workspace_id, current_user)
    return ApiResult.create(res)


@router.post("/default", response_model=ApiResult[Any])
def _set_or_unset_default(session: SessionDep, params: SetupDefaultModel,
        current_user: User = Depends(get_current_active_superuser)) -> Any:
    set_or_unset_default_model(session, params, current_user)
    return ApiResult.create()
