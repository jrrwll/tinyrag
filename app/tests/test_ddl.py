import logging

from sqlalchemy.schema import CreateTable
from sqlmodel import SQLModel, Session, create_engine, select

from app.config import settings
from app.entities.model import Model

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def test_ddl() -> None:
    print("\nTesting DDL")

    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    with Session(engine) as session:
        session.exec(select(1))

    for table in SQLModel.metadata.tables.values():
        c = CreateTable(table).compile(engine)
        print(c.string)


if __name__ == "__main__":
    test_ddl()
