import json
from typing import Any

from fastapi import APIRouter

from app.common.deps import SessionDep
from app.common.error_code import BizException, ErrorCode
from app.entities.model import Model
from app.schemas.model import ModelCreate, ModelPublic

router = APIRouter(prefix="/model", tags=["model"])


@router.get("/", response_model=ModelPublic)
def get(session: SessionDep, id: int) -> Any:
    item = session.get(Model, id)
    if not item:
        raise BizException.new(ErrorCode.model_not_found)

    resp = ModelPublic(**item.model_dump(exclude_unset=True))
    if item.settings:
        resp.settings = json.loads(item.settings)
    return resp


@router.post("/", response_model=ModelPublic)
def create(session: SessionDep, model_in: ModelCreate) -> Any:
    item = Model.model_validate(model_in)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item
