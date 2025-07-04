from typing import Any

from fastapi import APIRouter, Query

from app.common.base import PageResult
from app.common.config import settings
from app.common.deps import SessionDep
from app.common.error_code import BizException, ErrorCode
from app.core.model.api import (
    ModelCreate,
    ModelPublic,
    ModelTestRun,
    ModelTestRunPublic,
    ModelUpdate,
)
from app.core.model.privoder.base import get_model_provider
from app.entities.dao.model import page_and_count_models
from app.entities.model import Model

router = APIRouter(prefix="/model", tags=["model"])


@router.get("/list", response_model=PageResult[ModelPublic])
def list(
    session: SessionDep,
    page_no: int = Query(default=1, ge=1, le=10000),
    page_size: int = settings.DEFAULT_PAGE_NODE,
) -> Any:
    entities, count = page_and_count_models(session, page_no, page_size)
    return PageResult[ModelPublic](
        page_no=page_no,
        page_size=page_size,
        total=count,
        items=[ModelPublic.new(entity) for entity in entities],
    )


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
        raise BizException.new(ErrorCode.model_not_found, params.id)

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

    model = ModelPublic.new(entity)
    provider = get_model_provider(model)
    result = provider.test_run(params.prompt)
    return ModelTestRunPublic(result=result)
