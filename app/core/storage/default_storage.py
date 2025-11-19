from sqlmodel import Session

from app.common.error_code import BizException, ErrorCode
from app.core.storage.api import StoragePublic
from app.entities.dao.storage import get_storage, get_tenant_default_storage


def get_default_storage(session: Session, storage_id: int | None,
        tenant_id: int) -> StoragePublic:
    if not storage_id:
        default_storage = get_tenant_default_storage(session, None, tenant_id)
        if not default_storage or default_storage.storage_id is None:
            raise BizException.create(ErrorCode.storage_not_set)
        storage_id = default_storage.storage_id

    storage_entity = get_storage(session, storage_id, tenant_id)
    if not storage_entity:
        raise BizException.create(
            ErrorCode.storage_id_not_found, id=storage_id
        )
    return StoragePublic.create(storage_entity)
