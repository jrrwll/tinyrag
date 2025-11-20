from typing import Annotated, Any, Optional

from fastapi import Depends

from app.api import CustomAPIRouter
from app.common.deps import CurrentUser, SessionDep, \
    get_current_active_superuser
from app.common.error_code import BizException, ErrorCode
from app.config import settings
from app.core.meta.service import ProviderMetaService
from app.core.storage.api import SetupDefaultStorage, StorageCreate, \
    StoragePublic, \
    StorageSimplePublic, StorageUpdate, StorageUpdateConfig
from app.core.storage.service import create_storage, delete_storage, \
    find_default_storage, set_or_unset_default_storage, update_storage, \
    update_storage_config
from app.entities.dao.storage import get_storage, page_and_count_storages
from app.entities.user import User
from corepy.api.result import ApiResult, IdResult, PageResult

router = CustomAPIRouter(prefix="/storage", tags=["storage"])


@router.get("/list", response_model=ApiResult[PageResult[StorageSimplePublic]])
def _list(
        session: SessionDep,
        current_user: CurrentUser,
        page_no: Annotated[int, settings.page_no_query],
        page_size: Annotated[int, settings.page_size_query],
) -> Any:
    entities, count = page_and_count_storages(
        session, page_no, page_size, current_user.tenant_id)
    res = PageResult[StorageSimplePublic](
        page_no=page_no,
        page_size=page_size,
        total=count,
        items=[StorageSimplePublic(**entity) for entity in entities],
    )
    return ApiResult.ok(res)


@router.get("", response_model=ApiResult[StoragePublic])
def _get(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    entity = get_storage(session, id, current_user.tenant_id)
    if not entity:
        raise BizException.create(ErrorCode.storage_not_found)

    res = StoragePublic.create(entity)
    ProviderMetaService.from_storage().desensitizing_config_dict(
        res.type, res.config)
    return ApiResult.ok(res)


@router.post("", response_model=ApiResult[IdResult])
def _create(session: SessionDep, params: StorageCreate,
        current_user: User = Depends(get_current_active_superuser)) -> Any:
    res = create_storage(session, params, current_user)
    return ApiResult.ok(res)


@router.put("/config",
            response_model=ApiResult[Any])
def _update_config(session: SessionDep, current_user: CurrentUser,
        params: StorageUpdateConfig) -> Any:
    res = update_storage_config(session, params, current_user)
    return ApiResult.ok(res)


@router.put("", response_model=ApiResult[Any])
def _update(session: SessionDep, current_user: CurrentUser,
        params: StorageUpdate) -> Any:
    update_storage(session, params, current_user)
    return ApiResult.ok()


@router.delete("", response_model=ApiResult[Any])
def _delete(session: SessionDep, id: int,
        current_user: User = Depends(get_current_active_superuser)) -> Any:
    delete_storage(session, id, current_user)
    return ApiResult.ok()


@router.get("/default", response_model=ApiResult[Optional[StoragePublic]])
def _get_default(session: SessionDep, current_user: CurrentUser,
        workspace_id: int | None = None) -> Any:
    res = find_default_storage(session, workspace_id, current_user)
    if res:
        ProviderMetaService.from_storage().desensitizing_config_dict(
            res.type, res.config)
    return ApiResult.ok(res)


@router.post("/default", response_model=ApiResult[Any])
def _set_or_unset_default(session: SessionDep, params: SetupDefaultStorage,
        current_user: User = Depends(get_current_active_superuser)) -> Any:
    set_or_unset_default_storage(session, params, current_user)
    return ApiResult.ok()
