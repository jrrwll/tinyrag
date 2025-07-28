from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from jwt.exceptions import InvalidTokenError

from passlib.context import CryptContext

from app.config import settings
from app.core.user.base import TokenPayload

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(
        subject: str | Any,
        expire_delta: timedelta = settings.token_expire_timedelta) -> str:
    expire = datetime.now(timezone.utc) + expire_delta
    to_encode = TokenPayload(exp=expire, sub=subject)

    return jwt.encode(
        to_encode.model_dump(exclude_none=True),
        settings.SECRET_KEY,
        algorithm=settings.SECRET_ALGORITHM)


def generate_password_reset_token(
        email: str,
        expire_delta: timedelta = settings.token_reset_expire_timedelta) -> str:
    now = datetime.now(timezone.utc)
    expire = now + expire_delta
    to_encode = TokenPayload(exp=expire, sub=email, nbf=now)

    return jwt.encode(
        to_encode.model_dump(exclude_none=True),
        settings.SECRET_KEY,
        algorithm=settings.SECRET_ALGORITHM)


def verify_password_reset_token(token: str) -> str | None:
    try:
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY, algorithm=settings.SECRET_ALGORITHM
        )
        return str(decoded_token["sub"])
    except InvalidTokenError:
        return None
