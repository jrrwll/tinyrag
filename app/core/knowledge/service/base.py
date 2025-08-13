from sqlmodel import Session

from app.common.error_code import BizException, ErrorCode
from app.config import settings
from app.core.knowledge.api import KnowledgeCreate, KnowledgeUpdate, \
    KnowledgeUpdateConfig
from app.core.knowledge.base import EmbeddingModelConfig
from app.core.model.base import LlmModelConfig
from app.core.model.enums import ModelType
from app.core.vector_store.base import VectorStoreConfig
from app.core.workspace.check_config import check_embedding_model_config, \
    check_llm_model_config, check_retrieval_model_config, \
    check_vector_store_config
from app.entities.dao.knowledge import get_knowledge
from app.entities.repo.model import get_setup_model
from app.entities.repo.vector_store import get_setup_vector_store
from app.entities.user import User
from app.util.api import IdResult


def create_knowledge(session: Session, params: KnowledgeCreate,
        current_user: User) -> IdResult:
    workspace_id, tenant_id = params.workspace_id, current_user.tenant_id

    if not params.process_rule:
        params.process_rule = settings.DEFAULT_PROCESS_RULE
    if not params.llm_model_config:
        model = get_setup_model(session, ModelType.LLM, workspace_id, tenant_id)
        if model:
            params.llm_model_config = LlmModelConfig(model_id=model.id)
    else:
        check_llm_model_config(session, params.llm_model_config, current_user)

    if not params.embedding_model_config:
        model = get_setup_model(session, ModelType.TextEmbedding, workspace_id, tenant_id)
        if model:
            params.embedding_model_config = EmbeddingModelConfig(
                model_id=model.id, model_name=model.model_name)
    else:
        check_embedding_model_config(session, params.embedding_model_config, current_user)

    if not params.vector_store_config:
        vector_store = get_setup_vector_store(session, workspace_id, tenant_id)
        if vector_store:
            params.vector_store_config = VectorStoreConfig(
                vector_store_id=vector_store.id)
    else:
        check_vector_store_config(session, params.vector_store_config, current_user)

    if params.retrieval_model_config:
        check_retrieval_model_config(session, params.retrieval_model_config, current_user)

    entity = params.to_entity()
    entity.tenant_id = tenant_id

    session.add(entity)
    session.commit()
    session.refresh(entity)
    return IdResult(id=entity.id)


def update_knowledge(session: Session, params: KnowledgeUpdate,
        current_user: User):
    id = params.id
    entity = get_knowledge(session, id, current_user.tenant_id)
    if not entity:
        raise BizException.create(ErrorCode.knowledge_not_found)

    params.update_entity(entity)

    session.add(entity)
    session.commit()


def update_knowledge_config(session: Session, params: KnowledgeUpdateConfig,
        current_user: User):
    id = params.id
    entity = get_knowledge(session, id, current_user.tenant_id)
    if not entity:
        raise BizException.create(ErrorCode.knowledge_not_found)

    # check
    if params.process_rule:
        entity.process_rule = params.process_rule.model_dump_json()

    if params.llm_model_config:
        check_llm_model_config(session, params.llm_model_config, current_user)
        entity.llm_model_config = params.llm_model_config.model_dump_json()

    if params.embedding_model_config:
        check_embedding_model_config(session, params.embedding_model_config,
                                     current_user)
        entity.embedding_model_config = params.embedding_model_config.model_dump_json()

    if params.vector_store_config:
        check_vector_store_config(session, params.vector_store_config,
                                  current_user)
        entity.vector_store_config = params.vector_store_config.model_dump_json()

    if params.retrieval_model_config:
        check_retrieval_model_config(session, params.retrieval_model_config,
                                     current_user)
        entity.retrieval_model_config = params.retrieval_model_config.model_dump_json()

    session.add(entity)
    session.commit()
