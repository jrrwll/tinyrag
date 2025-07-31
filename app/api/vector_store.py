from typing import Any, Optional

from fastapi import Depends

from app.api import CustomAPIRouter
from app.common.deps import CurrentUser, SessionDep, \
    get_current_active_superuser
from app.common.error_code import BizException, ErrorCode
from app.config import settings
from app.core.vector_store.api import SetupDefaultVectorStore, \
    VectorStoreCreate, VectorStorePublic
from app.core.vector_store.service import create_vector_store, \
    delete_vector_store, \
    find_default_vector_store, \
    set_or_unset_default_vector_store
from app.entities.dao.vector_store import get_vector_store, \
    page_and_count_vector_stores
from app.entities.user import User
from app.util.api import ApiResult, IdResult, PageResult

router = CustomAPIRouter(prefix="/vector-store", tags=["vectorstore"])


@router.get("/list", response_model=ApiResult[PageResult[VectorStorePublic]])
def list(
        session: SessionDep,
        current_user: CurrentUser,
        page_no: int = settings.page_no_query,
        page_size: int = settings.page_size_query,
) -> Any:
    entities, count = page_and_count_vector_stores(
        session, page_no, page_size, current_user.tenant_id)
    res = PageResult[VectorStorePublic](
        page_no=page_no,
        page_size=page_size,
        total=count,
        items=[VectorStorePublic.create(entity) for entity in entities],
    )
    return ApiResult.create(res)


@router.get("", response_model=ApiResult[VectorStorePublic])
def get(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    entity = get_vector_store(session, id, current_user.tenant_id)
    if not entity:
        raise BizException.create(ErrorCode.vector_store_not_found, id)

    return ApiResult.create(VectorStorePublic.create(entity))


@router.post("", response_model=ApiResult[IdResult])
def create(session: SessionDep, params: VectorStoreCreate,
        current_user: User = Depends(get_current_active_superuser)) -> Any:
    res = create_vector_store(session, params, current_user)
    return ApiResult.create(res)


@router.delete("", response_model=ApiResult[Any])
def delete(session: SessionDep, id: int,
        current_user: User = Depends(get_current_active_superuser)) -> Any:
    entity = get_vector_store(session, id, current_user.tenant_id)
    if not entity:
        raise BizException.create(ErrorCode.vector_store_not_found, id)

    delete_vector_store(session, id, current_user)
    return ApiResult.create()


@router.get("/default", response_model=ApiResult[Optional[VectorStorePublic]])
def get_default(session: SessionDep, current_user: CurrentUser,
        workspace_id: int | None = None) -> Any:
    res = find_default_vector_store(session, workspace_id, current_user)
    return ApiResult.create(res)


@router.post("/default", response_model=ApiResult[Any])
def set_or_unset_default(session: SessionDep, params: SetupDefaultVectorStore,
        current_user: User = Depends(get_current_active_superuser)) -> Any:
    set_or_unset_default_vector_store(session, params, current_user)
    return ApiResult.create()
