from typing import Any

from fastapi import APIRouter, Query
from sqlmodel import select

from app.common.base import ApiResult, IdResult, PageResult
from app.common.deps import SessionDep
from app.common.error_code import BizException, ErrorCode
from app.config import settings
from app.core.model.api import (
    ModelCreate,
    ModelPublic,
    ModelTestRun,
    ModelTestRunPublic,
    ModelUpdate, ModelUpdateEnablePublic, SetupDefaultModel,
)
from app.core.model.enums import ModelType
from app.core.model.privoder.base import get_model_provider
from app.entities.dao.model import page_and_count_models
from app.entities.model import DefaultModel, Model

router = APIRouter(prefix="/model", tags=["model"])


@router.get("/list", response_model=ApiResult[PageResult[ModelPublic]])
def list(
    session: SessionDep,
    page_no: int = Query(default=1, ge=1, le=settings.DEFAULT_MAX_PAGE_NO),
    page_size: int = Query(default=settings.DEFAULT_PAGE_SIZE,
                           ge=1, le=settings.DEFAULT_MAX_PAGE_SIZE),
) -> Any:
    entities, count = page_and_count_models(session, page_no, page_size)
    res = PageResult[ModelPublic](
        page_no=page_no,
        page_size=page_size,
        total=count,
        items=[ModelPublic.new(entity) for entity in entities],
    )
    return ApiResult.new(res)


@router.get("", response_model=ApiResult[ModelPublic])
def get(session: SessionDep, id: int) -> Any:
    entity = session.get(Model, id)
    if not entity:
        raise BizException.new(ErrorCode.model_not_found, id)

    return ApiResult.new(ModelPublic.new(entity))


@router.post("", response_model=ApiResult[IdResult])
def create(session: SessionDep, params: ModelCreate) -> Any:
    entity = params.to_entity()

    session.add(entity)
    session.commit()
    session.refresh(entity)

    return ApiResult.new(IdResult(id=entity.id))


@router.put("", response_model=ApiResult[Any])
def update(session: SessionDep, params: ModelUpdate) -> Any:
    entity = session.get(Model, params.id)
    if not entity:
        raise BizException.new(ErrorCode.model_not_found, params.id)

    params.update_entity(entity)

    session.add(entity)
    session.commit()

    return ApiResult.new()


@router.post("/update_enable", response_model=ApiResult[ModelUpdateEnablePublic])
def update_enable(session: SessionDep, id: int) -> Any:
    entity = session.get(Model, id)
    if not entity:
        raise BizException.new(ErrorCode.model_not_found, id)

    entity.enable = not entity.enable
    session.add(entity)
    session.commit()
    session.refresh(entity)

    return ApiResult.new(ModelUpdateEnablePublic(
        id=id, enable=entity.enable))


@router.delete("", response_model=ApiResult[Any])
def delete(session: SessionDep, id: int) -> Any:
    entity = session.get(Model, id)
    if not entity:
        raise BizException.new(ErrorCode.model_not_found, id)

    session.delete(entity)
    session.commit()
    return ApiResult.new()


@router.post("/test_run", response_model=ApiResult[ModelTestRunPublic])
def test_run(session: SessionDep, params: ModelTestRun) -> Any:
    entity = session.get(Model, params.id)
    if not entity:
        raise BizException.new(ErrorCode.model_not_found, params.id)

    model = ModelPublic.new(entity)
    provider = get_model_provider(model)
    result = provider.test_run(params.prompt)
    return ApiResult.new(ModelTestRunPublic(result=result))


@router.get("/default_model", response_model=ApiResult[ModelPublic])
def get_default_model(session: SessionDep, model_type: ModelType) -> Any:
    default_model = _find_default_model(session, model_type)
    if default_model and default_model.model_id:
        model_id = default_model.model_id
        model_entity = session.get(Model, model_id)
        if not model_entity:
            raise BizException.new(ErrorCode.model_not_found, model_id)
        return ApiResult.new(ModelPublic.new(model_entity))
    return ApiResult.new()


@router.post("/default_model", response_model=ApiResult[Any])
def set_or_unset_default_model(session: SessionDep, params: SetupDefaultModel) -> Any:
    model_id, model_type = params.model_id, params.model_type
    if not model_id and not model_type:
        raise BizException.new(ErrorCode.request_validation_error_detail,
                               'neither model_id or model_type is unset')

    # unset case
    if model_type:
        entity = _find_default_model(session, model_type)
        if not entity:
            return ApiResult.new()

        entity.model_id = None
        session.add(entity)
        session.commit()
        session.refresh(entity)
        return ApiResult.new()

    # set case
    model_entity = session.get(Model, model_id)
    if not model_entity:
        raise BizException.new(ErrorCode.model_not_found, model_id)

    model_type = model_entity.type
    entity = _find_default_model(session, model_type)
    if entity:
        entity.model_id = model_id
    else:
        entity = DefaultModel(model_type=model_entity, model_id=model_id)

    session.add(entity)
    session.commit()
    session.refresh(entity)
    return ApiResult.new()


def _find_default_model(session: SessionDep, model_type: ModelType
) -> DefaultModel | None:
    select_statement = select(DefaultModel).where(
        DefaultModel.model_type == model_type)
    return session.exec(select_statement).one()
