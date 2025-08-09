from typing import Any

from fastapi import Depends

from app.api import CustomAPIRouter
from app.common.deps import CurrentUser, SessionDep, \
    get_current_active_superuser
from app.common.error_code import BizException, ErrorCode
from app.config import settings
from app.core.workspace.api import SimpleWorkspacePublic, WorkspaceCreate, \
    WorkspacePublic, WorkspaceUnsetConfig, WorkspaceUpdate, \
    WorkspaceUpdateConfig
from app.core.workspace.service import config_workspace, \
    create_workspace, \
    unset_config_workspace, update_workspace
from app.entities.dao.workspace import get_workspace, page_and_count_workspaces
from app.entities.user import User
from app.util.api import ApiResult, IdResult, PageResult

router = CustomAPIRouter(prefix="/workspace", tags=["workspace"])


@router.get("/list",
            response_model=ApiResult[PageResult[SimpleWorkspacePublic]])
def _list(
        session: SessionDep,
        current_user: CurrentUser,
        page_no: int = settings.page_no_query,
        page_size: int = settings.page_size_query,
) -> Any:
    entities, count = page_and_count_workspaces(
        session, page_no, page_size, current_user.tenant_id)
    res = PageResult[SimpleWorkspacePublic](
        page_no=page_no,
        page_size=page_size,
        total=count,
        items=[SimpleWorkspacePublic(**entity) for entity in entities],
    )
    return ApiResult.create(res)


@router.get("", response_model=ApiResult[WorkspacePublic])
def _get(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    entity = get_workspace(session, id, current_user.tenant_id)
    if not entity:
        raise BizException.create(ErrorCode.workspace_not_found)

    return ApiResult.create(WorkspacePublic.create(entity))


@router.post("", response_model=ApiResult[IdResult])
def _create(session: SessionDep, params: WorkspaceCreate,
        current_user: User = Depends(get_current_active_superuser)) -> Any:
    workspace_id = create_workspace(session, params, current_user)
    return ApiResult.create(IdResult(id=workspace_id))


@router.put("", response_model=ApiResult[Any])
def _update(session: SessionDep, current_user: CurrentUser,
        params: WorkspaceUpdate) -> Any:
    update_workspace(session, params, current_user)
    return ApiResult.create()


@router.post("/config", response_model=ApiResult[Any])
def _config(session: SessionDep, current_user: CurrentUser,
        params: WorkspaceUpdateConfig) -> Any:
    config_workspace(session, params, current_user)
    return ApiResult.create()


@router.delete("/config", response_model=ApiResult[Any])
def _config(session: SessionDep, current_user: CurrentUser,
        params: WorkspaceUnsetConfig) -> Any:
    unset_config_workspace(session, params, current_user)
    return ApiResult.create()
