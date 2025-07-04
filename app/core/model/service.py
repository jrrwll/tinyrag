from functools import lru_cache

from sqlmodel import Session

from app.common.db import engine
from app.common.error_code import BizException, ErrorCode
from app.core.model.api import ModelPublic
from app.entities.model import Model


@lru_cache(maxsize=1000)
def get_model(id: int) -> ModelPublic:
    with Session(engine) as session:
        entity = session.get(Model, id)
        if not entity:
            raise BizException.new(ErrorCode.model_not_found, id)

        return ModelPublic.new(entity)
