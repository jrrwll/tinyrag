from sqlalchemy.orm.session import Session

from app.common.error_code import BizException, ErrorCode
from app.core.user.enums import UserRole
from app.core.workspace.api import WorkspaceCreate, WorkspaceUnsetConfig, \
    WorkspaceUpdate, \
    WorkspaceUpdateConfig
from app.core.workspace.check_config import check_embedding_model_config, \
    check_llm_model_config, check_retrieval_model_config, \
    check_vector_store_config
from app.entities.dao.user import get_workspace_permission
from app.entities.dao.workspace import get_workspace, get_workspace_by_name
from app.entities.user import User


def create_workspace(session: Session, params: WorkspaceCreate,
        current_user: User) -> int:
    entity = get_workspace_by_name(session, params.name, current_user.tenant_id)
    if entity:
        raise BizException.create(
            ErrorCode.workspace_name_already_exists, params.name)

    entity = params.to_entity()
    entity.tenant_id = current_user.tenant_id

    session.add(entity)
    session.commit()
    session.refresh(entity)
    return entity.id


def update_workspace(session: Session, params: WorkspaceUpdate,
        current_user: User):
    entity = get_workspace(session, params.id, current_user.tenant_id)
    if not entity:
        raise BizException.create(ErrorCode.workspace_not_found, params.id)

    # check permission
    _check_workspace_permission(session, params.id, current_user)

    # check name
    if entity.name != params.name:
        entity = get_workspace_by_name(
            session, params.name, current_user.tenant_id)
        if entity:
            raise BizException.create(
                ErrorCode.workspace_name_already_exists, params.name)

    params.update_entity(entity)

    session.add(entity)
    session.commit()


def config_workspace(
        session: Session, params: WorkspaceUpdateConfig,
        current_user: User):
    if (not params.llm_model_config
            and not params.embedding_model_config
            and not params.vector_store_config
            and not params.retrieval_model_config):
        raise BizException.create(ErrorCode.request_validation_error, "any config param is required")

    entity = get_workspace(session, params.id, current_user.tenant_id)
    if not entity:
        raise BizException.create(ErrorCode.workspace_not_found, params.id)

    # check permission
    _check_workspace_permission(session, params.id, current_user)

    # check model
    if params.llm_model_config:
        check_llm_model_config(session, params.llm_model_config, current_user)
        entity.llm_model_config = params.llm_model_config.model_dump_json()

    if params.embedding_model_config:
        check_embedding_model_config(session, params.embedding_model_config, current_user)
        entity.embedding_model_config = params.embedding_model_config.model_dump_json()

    if params.vector_store_config:
        check_vector_store_config(session, params.vector_store_config, current_user)
        entity.vector_store_config = params.vector_store_config.model_dump_json()

    if params.retrieval_model_config:
        check_retrieval_model_config(session, params.retrieval_model_config, current_user)
        entity.retrieval_model_config = params.retrieval_model_config.model_dump_json()

    session.add(entity)
    session.commit()


def unset_config_workspace(
        session: Session, params: WorkspaceUnsetConfig,
        current_user: User):
    if (not params.llm_model_config
            and not params.embedding_model_config
            and not params.vector_store_config
            and not params.retrieval_model_config):
        raise BizException.create(ErrorCode.request_validation_error, "any config param is required")

    entity = get_workspace(session, params.id, current_user.tenant_id)
    if not entity:
        raise BizException.create(ErrorCode.workspace_not_found, params.id)

    # check permission
    _check_workspace_permission(session, params.id, current_user)

    if params.llm_model_config:
        entity.llm_model_config = None
    if params.embedding_model_config:
        entity.embedding_model_config = None
    if params.vector_store_config:
        entity.vector_store_config = None
    if params.retrieval_model_config:
        entity.retrieval_model_config = None

    session.add(entity)
    session.commit()


def _check_workspace_permission(session: Session, workspace_id: int,
        current_user: User):
    if current_user.is_superuser:
        return

    permission = get_workspace_permission(session, workspace_id, current_user)
    if (not permission or not permission.role
            or not permission.role.implies(UserRole.Admin)):
        raise BizException.create(ErrorCode.insufficient_permissions)
