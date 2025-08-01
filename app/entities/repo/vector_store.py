from sqlmodel import Session

from app.common.error_code import BizException, ErrorCode
from app.core.vector_store.api import VectorStorePublic
from app.entities.dao.vector_store import get_default_vector_store, \
    get_vector_store


def get_setup_vector_store(session: Session, workspace_id: int, tenant_id: int) -> VectorStorePublic:
    entity = get_default_vector_store(session, workspace_id, tenant_id)
    if not entity or entity.is_unset():
        entity = get_default_vector_store(session, None, tenant_id)
    if not entity or entity.is_unset():
        raise BizException.create(ErrorCode.default_vector_store_not_set)

    model_entity = get_vector_store(session, entity.vector_store_id, tenant_id)
    if not model_entity:
        raise BizException.create(ErrorCode.vector_store_not_found, entity.model_id)
    return VectorStorePublic.create(model_entity)
