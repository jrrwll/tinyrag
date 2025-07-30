from typing import Sequence

from pydantic import EmailStr
from sqlmodel import Session, func, select

from app.core.user.enums import PermissionResourceType
from app.entities.user import Permission, User


def get_user_by_email(session: Session, email: EmailStr | str,
        include_deleted: bool = False) -> User | None:
    conditions = [User.email == str(email)]
    if include_deleted:
        conditions.append(User.is_deleted == False)

    statement = select(User).where(*conditions)
    return session.exec(statement).first()


def page_and_count_users(session: Session,
        page_no: int, page_size: int, tenant_id: int
) -> tuple[Sequence[User], int]:
    conditions = [User.tenant_id == tenant_id]

    count_statement = (
        select(func.count()).select_from(User).where(*conditions)
    )
    count = session.exec(count_statement).one()

    offset = (page_no - 1) * page_size
    limit = page_size

    page_statement = (
        select(User)
        .where(*conditions)
        .order_by(User.updated_at.desc())
        .offset(offset)
        .limit(limit)
    )
    entities = session.exec(page_statement).all()
    return entities, count


def get_permission(session: Session,
        resource_type: PermissionResourceType, resource_id: int,
        user_identify: str, tenant_id: int
) -> Permission | None:
    conditions = [
        Permission.tenant_id == tenant_id,
        Permission.resource_type == resource_type,
        Permission.resource_id == resource_id,
        Permission.user_identify == user_identify,
    ]

    statement = select(Permission).where(*conditions)
    return session.exec(statement).first()


def page_and_count_permissions(session: Session,
        page_no: int, page_size: int,
        resource_type: PermissionResourceType, tenant_id: int
) -> tuple[Sequence[Permission], int]:
    conditions = [
        Permission.resource_type == resource_type,
        Permission.tenant_id == tenant_id,
    ]

    count_statement = (
        select(func.count()).select_from(Permission).where(*conditions)
    )
    count = session.exec(count_statement).one()

    offset = (page_no - 1) * page_size
    limit = page_size

    page_statement = (
        select(Permission)
        .where(*conditions)
        .order_by(Permission.updated_at.desc())
        .offset(offset)
        .limit(limit)
    )
    entities = session.exec(page_statement).all()
    return entities, count
