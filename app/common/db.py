from sqlmodel import create_engine

from app.common.config import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
