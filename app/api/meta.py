from typing import Any

from app.api import CustomAPIRouter
from app.core.meta.api import MetaBaseEntity
from app.core.meta.provider import list_model_providers, \
    list_vector_store_providers
from app.core.model.enums import ModelType
from app.util.api import ApiResult, ListResult

router = CustomAPIRouter(prefix="/meta", tags=["meta"])


@router.get("/model/providers",
            response_model=ApiResult[ListResult[MetaBaseEntity]])
def _list_model_provider(model_type: ModelType) -> Any:
    res = list_model_providers(model_type)
    return ApiResult.create(ListResult.create(res))


@router.get("/vector-store/providers",
            response_model=ApiResult[ListResult[MetaBaseEntity]])
def _list_vector_store_provider():
    res = list_vector_store_providers()
    return ApiResult.create(ListResult.create(res))
