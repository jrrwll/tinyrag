from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import ValidationError

from app.common.error_code import BizException, ErrorCode
from app.config import settings
from app.core.user.base import TokenPayload

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def encode_access_token(payload: TokenPayload) -> str:
    return jwt.encode(
        payload.model_dump(exclude_none=True),
        settings.ACCESS_TOKEN_PRIVATE_KEY,
        algorithm=settings.ACCESS_TOKEN_ALGORITHM)


def decode_access_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(
            token, settings.ACCESS_TOKEN_PUBLIC_KEY,
            algorithms=[settings.ACCESS_TOKEN_ALGORITHM]
        )
        return TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise BizException.create(ErrorCode.invalid_credentials)


def create_access_token(
        subject: str,
        expire_delta: timedelta = settings.token_expire_timedelta) -> str:
    expire = datetime.now(timezone.utc) + expire_delta
    payload = TokenPayload(exp=expire, sub=subject)
    return encode_access_token(payload)


def generate_password_reset_token(
        email: str,
        expire_delta: timedelta = settings.token_reset_expire_timedelta) -> str:
    now = datetime.now(timezone.utc)
    expire = now + expire_delta
    payload = TokenPayload(exp=expire, sub=email, nbf=now)
    return encode_access_token(payload)


def verify_password_reset_token(token: str) -> str | None:
    try:
        payload = decode_access_token(token)
        return payload.sub
    except BizException:
        return None
