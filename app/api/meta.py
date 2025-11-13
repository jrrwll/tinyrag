from typing import Any

from app.api import CustomAPIRouter
from app.core.meta.api import MetaBaseEntity
from app.core.meta.service import ProviderMetaService
from app.core.model.enums import ModelType
from corepy.api.result import ApiResult, ListResult

router = CustomAPIRouter(prefix="/meta", tags=["meta"])


@router.get("/model/providers",
            response_model=ApiResult[ListResult[MetaBaseEntity]])
def _list_model_provider(model_type: ModelType) -> Any:
    res = ProviderMetaService.from_model(model_type).list()
    return ApiResult.create(ListResult.create(res))


@router.get("/vector-store/providers",
            response_model=ApiResult[ListResult[MetaBaseEntity]])
def _list_vector_store_provider():
    res = ProviderMetaService.from_vector_store().list()
    return ApiResult.create(ListResult.create(res))


@router.get("/storage/providers",
            response_model=ApiResult[ListResult[MetaBaseEntity]])
def _list_storage_provider():
    res = ProviderMetaService.from_storage().list()
    return ApiResult.create(ListResult.create(res))
