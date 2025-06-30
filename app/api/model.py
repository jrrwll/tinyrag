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

    item_dict = item.model_dump(exclude_none=True)
    item_dict['settings'] = json.loads(item.settings)
    return ModelPublic(**item_dict)




@router.post("/", response_model=ModelPublic)
def create(session: SessionDep, model_in: ModelCreate) -> Any:
    item = Model.model_validate(model_in, update={
        "base_url": model_in.settings.get("base_url"),
        "api_key": model_in.settings.get("api_key"),
        "settings": json.dumps(model_in.settings),
    })
    session.add(item)
    session.commit()
    session.refresh(item)

    item_dict = item.model_dump()
    item_dict["settings"] = json.loads(item_dict["settings"])
    return ModelPublic(**item_dict).model_dump()
