from sqlmodel import Session

from app.common.error_code import BizException, ErrorCode
from app.core.vector_store.api import VectorStorePublic
from app.core.vector_store.base import VectorStoreConfig
from app.entities.dao.vector_store import get_tenant_default_vector_store, \
    get_vector_store


def get_vector_store_from_config(session: Session, vector_store_config: VectorStoreConfig, tenant_id: int) -> VectorStorePublic:
    vector_store_id = vector_store_config.vector_store_id
    entity = get_vector_store(session, vector_store_id, tenant_id)
    if not entity:
        raise BizException.create(
            ErrorCode.vector_store_not_found)
    return VectorStorePublic.create(entity)


def get_setup_vector_store(session: Session, workspace_id: int, tenant_id: int,
        required: bool = False) -> VectorStorePublic | None:
    entity = get_tenant_default_vector_store(session, workspace_id, tenant_id)
    if not entity or entity.vector_store_id is None:
        entity = get_tenant_default_vector_store(session, None, tenant_id)
    if not entity or entity.vector_store_id is None:
        raise BizException.create(ErrorCode.vector_store_not_set)

    vector_store_id = entity.vector_store_id
    ref_entity = get_vector_store(session, vector_store_id, tenant_id)
    if not ref_entity:
        if required:
            raise BizException.create(
                ErrorCode.vector_store_id_not_found, id=vector_store_id)
        else:
            return None
    return VectorStorePublic.create(ref_entity)
