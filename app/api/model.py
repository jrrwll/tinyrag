from typing import Any, Optional

from app.api import CustomAPIRouter
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
from app.entities.model import Model
from app.util.api import ApiResult, IdResult, PageResult

router = CustomAPIRouter(prefix="/model", tags=["model"])


@router.get("/list", response_model=ApiResult[PageResult[ModelPublic]])
def list(
    session: SessionDep,
    page_no: int = settings.page_no_query,
    page_size: int = settings.page_size_query,
) -> Any:
    entities, count = page_and_count_models(session, page_no, page_size)
    res = PageResult[ModelPublic](
        page_no=page_no,
        page_size=page_size,
        total=count,
        items=[ModelPublic.create(entity) for entity in entities],
    )
    return ApiResult.create(res)


@router.get("", response_model=ApiResult[ModelPublic])
def get(session: SessionDep, id: int) -> Any:
    entity = session.get(Model, id)
    if not entity:
        raise BizException.create(ErrorCode.model_not_found, id)

    return ApiResult.create(ModelPublic.create(entity))


@router.post("", response_model=ApiResult[IdResult])
def create(session: SessionDep, params: ModelCreate) -> Any:
    entity = params.to_entity()

    session.add(entity)
    session.commit()
    session.refresh(entity)

    return ApiResult.create(IdResult(id=entity.id))


@router.put("", response_model=ApiResult[Any])
def update(session: SessionDep, params: ModelUpdate) -> Any:
    entity = session.get(Model, params.id)
    if not entity:
        raise BizException.create(ErrorCode.model_not_found, params.id)

    params.update_entity(entity)

    session.add(entity)
    session.commit()

    return ApiResult.create()


@router.post("/update-enable", response_model=ApiResult[ModelUpdateEnablePublic])
def update_enable(session: SessionDep, id: int) -> Any:
    entity = session.get(Model, id)
    if not entity:
        raise BizException.create(ErrorCode.model_not_found, id)

    entity.enable = not entity.enable
    session.add(entity)
    session.commit()
    session.refresh(entity)

    return ApiResult.create(ModelUpdateEnablePublic(
        id=id, enable=entity.enable))


@router.delete("", response_model=ApiResult[Any])
def delete(session: SessionDep, id: int) -> Any:
    entity = session.get(Model, id)
    if not entity:
        raise BizException.create(ErrorCode.model_not_found, id)

    session.delete(entity)
    session.commit()
    return ApiResult.create()


@router.post("/test-run", response_model=ApiResult[ModelTestRunPublic])
def test_run(session: SessionDep, params: ModelTestRun) -> Any:
    entity = session.get(Model, params.id)
    if not entity:
        raise BizException.create(ErrorCode.model_not_found, params.id)

    model = ModelPublic.create(entity)
    provider = get_model_provider(model)
    result = provider.test_run(params.prompt)
    return ApiResult.create(ModelTestRunPublic(result=result))


@router.get("/default-model", response_model=ApiResult[Optional[ModelPublic]])
def get_default_model(session: SessionDep, model_type: ModelType) -> Any:
    default_model = _find_default_model(session, model_type)
    if default_model and default_model.model_id:
        model_id = default_model.model_id
        model_entity = session.get(Model, model_id)
        if not model_entity:
            raise BizException.create(ErrorCode.model_not_found, model_id)
        return ApiResult.create(ModelPublic.create(model_entity))
    return ApiResult.create()


@router.post("/default-model", response_model=ApiResult[Any])
def set_or_unset_default_model(session: SessionDep, params: SetupDefaultModel) -> Any:
    model_id, model_type = params.model_id, params.model_type
    if not model_id and not model_type:
        raise BizException.create(ErrorCode.request_validation_error_detail,
                               'neither model_id or model_type is unset')

    # unset case
    if model_type:
        entity = _find_default_model(session, model_type)
        if not entity:
            return ApiResult.create()

        entity.model_id = None
        session.add(entity)
        session.commit()
        session.refresh(entity)
        return ApiResult.create()

    # set case
    model_entity = session.get(Model, model_id)
    if not model_entity:
        raise BizException.create(ErrorCode.model_not_found, model_id)

    model_type = model_entity.type
    entity = _find_default_model(session, model_type)
    if entity:
        entity.model_id = model_id
    else:
        entity = DefaultModel(model_type=model_type, model_id=model_id)

    session.add(entity)
    session.commit()
    session.refresh(entity)
    return ApiResult.create()


# def _find_default_model(session: SessionDep, model_type: ModelType
# ) -> DefaultModel | None:
#     select_statement = select(DefaultModel).where(
#         DefaultModel.model_type == model_type)
#     return session.exec(select_statement).one_or_none()
