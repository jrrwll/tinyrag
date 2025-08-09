from typing import Any

from fastapi import Depends

from app.api import CustomAPIRouter
from app.common.deps import CurrentUser, \
    get_current_active_superuser
from app.common.deps import SessionDep
from app.common.error_code import BizException, ErrorCode
from app.config import settings
from app.core.user.api import UserCreate, UserPublic, UserUpdate, \
    UserUpdateMe, UserUpdatePassword
from app.core.user.service import create_user, delete_user, update_my_password, \
    update_user
from app.entities.dao.user import get_user_by_email, page_and_count_users
from app.util.api import ApiResult, PageResult

router = CustomAPIRouter(prefix="/user", tags=["user"])


# for users
@router.get("/list", response_model=ApiResult[PageResult[UserPublic]],
            dependencies=[Depends(get_current_active_superuser)])
def list_users(session: SessionDep, current_user: CurrentUser,
        page_no: int = settings.page_no_query,
        page_size: int = settings.page_size_query) -> Any:
    entities, count = page_and_count_users(
        session, page_no, page_size, current_user.tenant_id)

    res = PageResult(
        page_no=page_no,
        page_size=page_size,
        total=count,
        items=[UserPublic.create(i) for i in entities],
    )
    return ApiResult.create(res)


@router.get("", response_model=ApiResult[UserPublic],
            dependencies=[Depends(get_current_active_superuser)])
def get_user(session: SessionDep, email: str) -> Any:
    entity = get_user_by_email(session, email)
    if not entity:
        raise BizException.create(ErrorCode.user_not_found)

    res = UserPublic.create(entity)
    return ApiResult.create(res)


@router.post("", response_model=ApiResult[UserPublic],
             dependencies=[Depends(get_current_active_superuser)])
def create(session: SessionDep, current_user: CurrentUser,
        params: UserCreate) -> Any:
    user = create_user(session, params, current_user)
    return ApiResult.create(user)


@router.put("", response_model=ApiResult[UserPublic],
            dependencies=[Depends(get_current_active_superuser)])
def update(session: SessionDep, params: UserUpdate) -> Any:
    user = update_user(session, params)
    return ApiResult.create(user)


@router.delete("", response_model=ApiResult[Any],
               dependencies=[Depends(get_current_active_superuser)])
def delete(session: SessionDep, email: str, current_user: CurrentUser) -> Any:
    delete_user(session, email, current_user)
    return ApiResult.create()


# for me
@router.get("/me", response_model=ApiResult[UserPublic])
def get_me(current_user: CurrentUser) -> Any:
    res = UserPublic.create(current_user)
    return ApiResult.create(res)


@router.put("/me", response_model=ApiResult[Any])
def update_me(session: SessionDep, params: UserUpdateMe,
        current_user: CurrentUser) -> Any:
    current_user.full_name = params.full_name
    current_user.avatar = params.avatar

    session.add(current_user)
    session.commit()

    return ApiResult.create()


@router.post("/me/update-password", response_model=ApiResult[Any])
def me_update_password(session: SessionDep, params: UserUpdatePassword,
        current_user: CurrentUser) -> Any:
    update_my_password(session, params, current_user)
    return ApiResult.create()
