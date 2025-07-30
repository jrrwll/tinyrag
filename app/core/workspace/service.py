from sqlalchemy.orm.session import Session

from app.common.error_code import BizException, ErrorCode
from app.core.model.enums import EmbeddingType, ModelType
from app.core.user.enums import UserRole
from app.core.workspace.api import WorkspaceCreate, WorkspaceUnsetConfig, \
    WorkspaceUpdate, \
    WorkspaceUpdateConfig
from app.entities.dao.model import get_model
from app.entities.dao.user import get_workspace_permission
from app.entities.dao.vector_store import get_vector_store
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
            and not params.vector_store_config):
        raise BizException.create(ErrorCode.request_validation_error_detail, "any config param is required")

    entity = get_workspace(session, params.id, current_user.tenant_id)
    if not entity:
        raise BizException.create(ErrorCode.workspace_not_found, params.id)

    # check permission
    _check_workspace_permission(session, params.id, current_user)

    # check model
    if params.llm_model_config:
        model_id = params.llm_model_config.model_id
        model_entity = get_model(session, model_id, current_user.tenant_id)
        if not model_entity:
            raise BizException.create(ErrorCode.model_not_found, model_id)
        elif model_entity.type != ModelType.LLM:
            raise BizException.create(
                ErrorCode.model_type_not_supported, model_entity.type.name)

        entity.llm_model_config = params.llm_model_config.model_dump_json()

    if params.embedding_model_config:
        embedding_type = params.embedding_model_config.embedding_type
        if embedding_type == EmbeddingType.Provider:
            model_id = params.embedding_model_config.model_id
            model_entity = get_model(session, model_id, current_user.tenant_id)
            if not model_entity:
                raise BizException.create(ErrorCode.model_not_found, model_id)
            elif model_entity.type != ModelType.TextEmbedding:
                raise BizException.create(
                    ErrorCode.model_type_not_supported, model_entity.type.name)
        else:
            # transformer
            model_name = params.embedding_model_config.model_name
            if not EmbeddingType.is_valid_model_name(model_name):
                raise BizException.create(
                    ErrorCode.model_name_not_supported, model_name)

        entity.embedding_model_config = params.embedding_model_config.model_dump_json()

    if params.vector_store_config:
        vector_store_id = params.vector_store_config.vector_id
        vector_store_entity = get_vector_store(
            session, vector_store_id, current_user.tenant_id)
        if not vector_store_entity:
            raise BizException.create(
                ErrorCode.vector_store_not_found, vector_store_id)

        entity.vector_store_config = params.vector_store_config.model_dump_json()

    session.add(entity)
    session.commit()


def unset_config_workspace(
        session: Session, params: WorkspaceUnsetConfig,
        current_user: User):
    if (not params.llm_model_config
            and not params.embedding_model_config
            and not params.vector_store_config):
        raise BizException.create(ErrorCode.request_validation_error_detail, "any config param is required")

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
