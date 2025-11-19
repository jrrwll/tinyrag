from sqlmodel import Session

from app.common.error_code import BizException, ErrorCode
from app.core.storage.api import StoragePublic
from app.entities.dao.storage import get_storage, get_tenant_default_storage


def get_setup_storage(session: Session, workspace_id: int, tenant_id: int,
        required: bool = False) -> StoragePublic | None:
    entity = get_tenant_default_storage(session, workspace_id, tenant_id)
    if not entity or entity.storage_id is None:
        entity = get_tenant_default_storage(session, None, tenant_id)
    if not entity or entity.storage_id is None:
        raise BizException.create(ErrorCode.storage_not_set)

    ref_entity = get_storage(session, entity.storage_id, tenant_id)
    if not ref_entity:
        if required:
            raise BizException.create(
                ErrorCode.storage_id_not_found, id=entity.storage_id)
        else:
            return None
    return StoragePublic.create(ref_entity)
