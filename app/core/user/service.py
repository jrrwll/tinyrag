import logging

from sqlmodel import Session

from app.common.error_code import BizException, ErrorCode
from app.common.security import create_access_token, \
    generate_password_reset_token, verify_password_reset_token
from app.common.security import get_password_hash, verify_password
from app.config import settings
from app.core.user.api import AccessTokenPublic, UserCreate, UserPublic, \
    UserResetPassword, UserUpdate, UserUpdatePassword
from app.core.user.email import generate_new_account_email, \
    generate_reset_password_email, send_email
from app.core.user.enums import UserRole
from app.entities.dao.user import get_user_by_email
from app.entities.user import User

logger = logging.getLogger(__name__)


def create_user(session: Session, params: UserCreate,
        current_user: User) -> UserPublic:
    user = get_user_by_email(session, params.email)
    if user:
        raise BizException.create(ErrorCode.user_email_already_exists)
    if params.email_domain != current_user.email_domain:
        raise BizException.create(ErrorCode.invalid_email_domain,
                                  params.email_domain)

    entity = User.model_validate(
        params, update={
            "name": params.name,
            "hashed_password": get_password_hash(params.password),
        })
    session.add(entity)
    session.commit()

    if settings.emails_enabled:
        subject, html_content = generate_new_account_email(
            email_to=params.email, username=params.name,
            password=params.password
        )
        send_email(
            email_to=params.email,
            subject=subject,
            html_content=html_content,
        )
    return UserPublic.create(entity)


def update_user(session: Session, params: UserUpdate) -> UserPublic:
    entity = get_user_by_email(session, params.email)
    if not entity:
        raise BizException.create(ErrorCode.user_not_found, params.email)

    entity.full_name = params.full_name
    entity.avatar = params.avatar
    session.add(entity)
    session.commit()

    return UserPublic.create(entity)


def update_my_password(session: Session, params: UserUpdatePassword,
        current_user: User):
    if not verify_password(params.current_password,
                           current_user.hashed_password):
        raise BizException.create(ErrorCode.email_or_password_incorrect)
    if params.current_password == params.new_password:
        raise BizException.create(ErrorCode.same_new_password)

    hashed_password = get_password_hash(params.new_password)
    current_user.hashed_password = hashed_password
    session.add(current_user)
    session.commit()


def delete_user(session: Session, email: str, current_user: User):
    entity = get_user_by_email(session, email)
    if not entity:
        raise BizException.create(ErrorCode.user_not_found, email)

    if email == current_user.email or entity.role == UserRole.Owner:
        raise BizException.create(ErrorCode.super_user_cannot_delete)

    entity.deleted = True
    session.add(entity)
    session.commit()
    logger.info(f"current_user {current_user.email} deleted user {email}")


def get_authenticated_user(session: Session, email: str,
        password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def generate_access_token(session: Session, username: str,
        password: str) -> AccessTokenPublic:
    user = get_authenticated_user(session, username, password)
    if not user:
        raise BizException.create(ErrorCode.email_or_password_incorrect)
    elif not user.is_active:
        raise BizException.create(ErrorCode.user_inactive)

    return AccessTokenPublic(
        access_token=create_access_token(user.email)
    )


def recover_user_password(session: Session, email: str):
    user = get_user_by_email(session, email)
    if not user:
        raise BizException.create(ErrorCode.user_not_found, email)

    password_reset_token = generate_password_reset_token(email)
    subject, html_content = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )
    send_email(
        email_to=user.email,
        subject=subject,
        html_content=html_content,
    )


def reset_user_password(session: Session, params: UserResetPassword):
    email = verify_password_reset_token(params.token)
    if not email:
        raise BizException.create(ErrorCode.invalid_token)

    user = get_user_by_email(session, email)
    if not user:
        raise BizException.create(ErrorCode.user_email_not_found)
    elif not user.is_active:
        raise BizException.create(ErrorCode.user_inactive)

    hashed_password = get_password_hash(password=params.new_password)
    user.hashed_password = hashed_password
    session.add(user)
    session.commit()
