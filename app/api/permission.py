from typing import Annotated, Any

from app.api import CustomAPIRouter
from app.common.deps import CurrentUser
from app.common.deps import SessionDep
from app.config import settings
from app.core.user.api import PermissionGrant, PermissionPublic, \
    PermissionRevoke
from app.core.user.enums import PermissionResourceType
from app.core.user.service import grant_permission, \
    revoke_permission
from app.entities.dao.user import page_and_count_permissions
from corepy.api.result import ApiResult, PageResult

router = CustomAPIRouter(prefix="/permission", tags=["permission"])


@router.get("/list",
            response_model=ApiResult[PageResult[PermissionPublic]])
def _list(
        session: SessionDep,
        current_user: CurrentUser,
        resource_type: PermissionResourceType,
        page_no: int = settings.page_no_query,
        page_size: int = settings.page_size_query,
) -> Any:
    entities, count = page_and_count_permissions(
        session, page_no, page_size, resource_type, current_user.tenant_id)
    res = PageResult[PermissionPublic](
        page_no=page_no,
        page_size=page_size,
        total=count,
        items=[PermissionPublic.create(entity) for entity in entities],
    )
    return ApiResult.ok(res)


@router.post("", response_model=ApiResult[Any])
def _grant(
        session: SessionDep,
        params: PermissionGrant,
        current_user: CurrentUser,
) -> Any:
    grant_permission(session, params, current_user)
    return ApiResult.ok()


@router.delete("", response_model=ApiResult[Any])
def _revoke(
        session: SessionDep,
        current_user: CurrentUser,
        params: PermissionRevoke,
) -> Any:
    revoke_permission(session, params, current_user)
    return ApiResult.ok()
