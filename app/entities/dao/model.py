# ruff: noqa: E712
from collections.abc import Sequence

from sqlmodel import func, select

from app.common.deps import SessionDep
from app.entities.model import Model


def page_and_count_models(
    session: SessionDep, page_no: int, page_size: int
) -> tuple[Sequence[Model], int]:
    count_statement = (
        select(func.count()).select_from(Model).where(Model.deleted == False)
    )
    count = session.exec(count_statement).one()

    offset = (page_no - 1) * page_size
    limit = page_size

    page_statement = (
        select(Model)
        .select_from(Model)
        .where(Model.deleted == False)
        .offset(offset)
        .limit(limit)
    )
    models = session.exec(page_statement).all()
    return models, count
