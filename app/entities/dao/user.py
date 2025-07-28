from sqlmodel import Session, select

from app.core.user.api import UserPublic
from app.entities.user import User


def get_user_by_email(session: Session, email: str,
        include_deleted: bool = False) -> User | None:
    conditions = [User.email == email]
    if include_deleted:
        conditions.append(User.is_deleted == False)

    statement = select(User).where(*conditions)
    session_user = session.exec(statement).first()
    return session_user


def page_and_count_users(session: Session,
        page_no: int, page_size: int) -> tuple[list[UserPublic], int]:
    pass
