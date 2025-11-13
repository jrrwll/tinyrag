from sqlmodel import Session

from app.common.error_code import BizException, ErrorCode
from app.core.meta.service import ProviderMetaService
from app.core.storage.api import SetupDefaultStorage, StorageCreate, \
    StoragePublic, StorageUpdate, StorageUpdateConfig
from app.entities.dao.storage import get_tenant_default_storage, get_storage
from app.entities.storage import TenantDefaultStorage
from app.entities.user import User
from corepy.api.result import ApiResult, IdResult


def create_storage(
        session: Session, params: StorageCreate,
        current_user: User) -> IdResult:
    # validate config
    meta_service = ProviderMetaService.from_storage()
    meta_service.validate_config_dict(params.type, params.config)
    meta_service.encrypt_config_dict(params.type, params.config)

    entity = params.to_entity()
    entity.tenant_id = current_user.tenant_id

    session.add(entity)
    session.commit()
    session.refresh(entity)

    return IdResult(id=entity.id)


def update_storage_config(session: Session, params: StorageUpdateConfig,
        current_user: User):
    tenant_id = current_user.tenant_id
    entity = get_storage(session, params.id, tenant_id)
    if not entity:
        raise BizException.create(ErrorCode.storage_not_found)

    # validate config
    meta_service = ProviderMetaService.from_storage()
    meta_service.validate_config_dict(entity.type, params.config)
    meta_service.encrypt_config_dict(entity.type, params.config)

    params.update_entity(entity)

    session.add(entity)
    session.commit()


def update_storage(session: Session, params: StorageUpdate, current_user: User):
    tenant_id = current_user.tenant_id
    entity = get_storage(session, params.id, tenant_id)
    if not entity:
        raise BizException.create(ErrorCode.storage_not_found)

    params.update_entity(entity)

    session.add(entity)
    session.commit()


def delete_storage(
        session: Session, storage_id: int,
        current_user: User):
    tenant_id = current_user.tenant_id
    entity = get_storage(session, storage_id, tenant_id)
    if not entity:
        raise BizException.create(ErrorCode.storage_not_found)

    default_entity = get_tenant_default_storage(session, None, tenant_id)
    if default_entity and default_entity.vector_store_id == storage_id:
        raise BizException.create(ErrorCode.vector_store_is_set_in_default)
    # TODO
    raise NotImplementedError()


def find_default_storage(
        session: Session, workspace_id: int | None, current_user: User
) -> StoragePublic | None:
    entity = get_tenant_default_storage(
        session, workspace_id, current_user.tenant_id)
    if not entity or entity.is_unset():
        if workspace_id:
            entity = get_tenant_default_storage(
                session, None, current_user.tenant_id)
        if not entity or entity.is_unset():
            return None

    storage_id = entity.storage_id
    storage_entity = get_storage(
        session, storage_id, current_user.tenant_id)
    if not storage_entity:
        raise BizException.create(
            ErrorCode.storage_id_not_found, id=storage_id)

    return StoragePublic.create(storage_entity)


def set_or_unset_default_storage(
        session: Session, params: SetupDefaultStorage,
        current_user: User):
    tenant_id = current_user.tenant_id
    workspace_id = params.workspace_id
    storage_id = params.storage_id

    entity = get_tenant_default_storage(session, workspace_id, tenant_id)

    # unset case
    if not storage_id:
        if not entity or entity.is_unset():
            return ApiResult.create()

        entity.storage_id = None

        session.add(entity)
        session.commit()
        return ApiResult.create()

    # set case
    if not entity:
        entity = TenantDefaultStorage(
            tenant_id=tenant_id,
        )
        if workspace_id:
            entity.workspace_id = workspace_id

    entity.storage_id = storage_id

    session.add(entity)
    session.commit()
