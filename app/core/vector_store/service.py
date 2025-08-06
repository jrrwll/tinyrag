from sqlmodel import Session

from app.common.error_code import BizException, ErrorCode
from app.core.meta.provider import validate_vector_store_config_dict
from app.core.vector_store.api import SetupDefaultVectorStore, \
    VectorStoreCreate, VectorStorePublic
from app.entities.dao.vector_store import get_default_vector_store, \
    get_vector_store
from app.entities.user import User
from app.entities.vector_store import TenantDefaultVectorStore
from app.util.api import ApiResult, IdResult


def create_vector_store(
        session: Session, params: VectorStoreCreate,
        current_user: User) -> IdResult:
    # validate config
    validate_vector_store_config_dict(params.type, params.config)

    entity = params.to_entity()
    entity.tenant_id = current_user.tenant_id

    session.add(entity)
    session.commit()
    session.refresh(entity)

    return IdResult(id=entity.id)


def delete_vector_store(
        session: Session, vector_store_id: int,
        current_user: User):
    default_entity = get_default_vector_store(session, current_user.tenant_id)
    if default_entity and default_entity.vector_store_id == vector_store_id:
        raise BizException.create(ErrorCode.vector_store_is_set_in_default)
    # TODO


def find_default_vector_store(
        session: Session, workspace_id: int | None, current_user: User
) -> VectorStorePublic | None:
    entity = get_default_vector_store(
        session, workspace_id, current_user.tenant_id)
    if not entity or entity.is_unset():
        if workspace_id:
            entity = get_default_vector_store(
                session, None, current_user.tenant_id)
            if not entity or entity.is_unset():
                return None

    vector_store_id = entity.vector_store_id
    vector_store_entity = get_vector_store(
        session, vector_store_id, current_user.tenant_id)
    if not vector_store_entity:
        raise BizException.create(
            ErrorCode.vector_store_not_found, vector_store_id)

    return VectorStorePublic.create(vector_store_entity)


def set_or_unset_default_vector_store(
        session: Session, params: SetupDefaultVectorStore,
        current_user: User):
    workspace_id = params.workspace_id
    vector_store_id = params.vector_store_id

    entity = get_default_vector_store(session, workspace_id, current_user.tenant_id)

    # unset case
    if not vector_store_id:
        if not entity or entity.is_unset():
            return ApiResult.create()

        entity.vector_store_id = None

        session.add(entity)
        session.commit()
        return ApiResult.create()

    # set case
    if not entity:
        entity = TenantDefaultVectorStore(
            tenant_id=current_user.tenant_id,
            workspace_id=workspace_id,
        )

    entity.vector_store_id = vector_store_id

    session.add(entity)
    session.commit()
