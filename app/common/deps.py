from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from sqlmodel import create_engine

from app.common.error_code import BizException, ErrorCode
from app.common.security import decode_access_token
from app.config import settings
from app.entities.dao.user import get_user_by_email
from app.entities.user import User

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]


def open_session() -> Session:
    return Session(engine)


reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_PREFIX_STR}/auth/access-token"
)
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    payload = decode_access_token(token)

    email = payload.sub
    user = get_user_by_email(session, email)
    if not user:
        raise BizException.create(ErrorCode.user_not_found, email)
    if not user.is_active:
        raise BizException.create(ErrorCode.user_inactive)
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise BizException.create(ErrorCode.insufficient_permissions)

    return current_user
