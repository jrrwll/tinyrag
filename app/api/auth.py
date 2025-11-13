from typing import Any

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.api import CustomAPIRouter
from app.common.deps import SessionDep
from app.core.user.api import AccessTokenPublic, UserResetPassword
from app.core.user.service import generate_access_token, recover_user_password, \
    reset_user_password
from corepy.api import ApiResult

router = CustomAPIRouter(prefix="/auth", tags=["auth"])


@router.post("/access-token", response_model=ApiResult[AccessTokenPublic])
def access_token(
        session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    res = generate_access_token(session, form_data.username, form_data.password)
    return ApiResult.create(res)


@router.post("/password-recovery", response_model=ApiResult[BaseModel])
def recover_password(session: SessionDep, email: str):
    recover_user_password(session, email)
    return ApiResult.create()


@router.post("/reset-password/", response_model=ApiResult[Any])
def reset_password(session: SessionDep, params: UserResetPassword) -> Any:
    reset_user_password(session, params)
    return ApiResult.create()
