# ruff: noqa: E712
from collections.abc import Sequence

from sqlmodel import Session
from sqlmodel import func, select

from app.common.db import engine
from app.common.db import SessionDep
from app.core.model.enums import ModelType
from app.entities.model import DefaultModel, Model


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


def get_default_models() -> dict[ModelType, Model]:
    with Session(engine) as session:
        select_all_statement = select(DefaultModel)
        default_models = session.exec(select_all_statement).all()

        model_ids = [default_model.id
                     for default_model in default_models]
        if not model_ids:
            return {}

        select_in_statement = select(Model).where(
            Model.id.in_(model_ids),
            Model.deleted == False
        )
        models = session.exec(select_in_statement).all()
        return {model.type: model for model in models}
