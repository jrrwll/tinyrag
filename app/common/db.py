from sqlmodel import create_engine, Session

from app.config import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def open_session() -> Session:
    return Session(engine)
