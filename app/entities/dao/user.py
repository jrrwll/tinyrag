from typing import Sequence
from pydantic import EmailStr
from sqlmodel import Session, func, select

from app.entities.user import User


def get_user_by_email(session: Session, email: EmailStr | str,
        include_deleted: bool = False) -> User | None:
    conditions = [User.email == str(email)]
    if include_deleted:
        conditions.append(User.is_deleted == False)

    statement = select(User).where(*conditions)
    session_user = session.exec(statement).first()
    return session_user


def page_and_count_users(session: Session,
        page_no: int, page_size: int, tenant_id: int
) -> tuple[Sequence[User], int]:
    conditions = [User.tenant_id == tenant_id, User.deleted == False]

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
    models = session.exec(page_statement).all()
    return models, count
