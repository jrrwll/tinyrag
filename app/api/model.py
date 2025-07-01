from typing import Any

from fastapi import APIRouter

from app.common.deps import SessionDep
from app.common.error_code import BizException, ErrorCode
from app.entities.model import Model
from app.schemas.model import (
    ModelCreate,
    ModelPublic,
    ModelTestRun,
    ModelTestRunPublic,
    ModelUpdate,
)
from app.services.model_service import test_run_model

router = APIRouter(prefix="/model", tags=["model"])


@router.get("", response_model=ModelPublic)
def get(session: SessionDep, id: int) -> Any:
    entity = session.get(Model, id)
    if not entity:
        raise BizException.new(ErrorCode.model_not_found, id)

    return ModelPublic.new(entity)


@router.post("", response_model=ModelPublic)
def create(session: SessionDep, params: ModelCreate) -> Any:
    entity = params.to_entity()

    session.add(entity)
    session.commit()
    session.refresh(entity)

    return ModelPublic.new(entity)


@router.put("", response_model=ModelPublic)
def update(session: SessionDep, params: ModelUpdate) -> Any:
    entity = session.get(Model, params.id)
    if not entity:
        raise BizException.new(ErrorCode.model_not_found, id)

    params.update_entity(entity)

    session.add(entity)
    session.commit()
    session.refresh(entity)

    return ModelPublic.new(entity)


@router.delete("")
def delete(session: SessionDep, id: int) -> Any:
    entity = session.get(Model, id)
    if not entity:
        raise BizException.new(ErrorCode.model_not_found, id)

    session.delete(entity)
    session.commit()
    return {"id": id}


@router.post("/update_enable", response_model=dict)
def update_enable(session: SessionDep, id: int) -> Any:
    entity = session.get(Model, id)
    if not entity:
        raise BizException.new(ErrorCode.model_not_found, id)

    entity.enable = not entity.enable
    session.add(entity)
    session.commit()
    session.refresh(entity)

    return {"id": id, "enable": entity.enable}


@router.post("/test_run", response_model=ModelTestRunPublic)
def test_run(session: SessionDep, params: ModelTestRun) -> Any:
    entity = session.get(Model, params.id)
    if not entity:
        raise BizException.new(ErrorCode.model_not_found, id)

    return test_run_model(session, params, entity)
