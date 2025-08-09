from sqlmodel import Session

from app.common.error_code import BizException, ErrorCode
from app.core.knowledge.base import EmbeddingModelConfig, RetrievalModelConfig
from app.core.model.base import LlmModelConfig
from app.core.model.builtin_models import is_valid_model_name
from app.core.model.enums import ModelType
from app.core.vector_store.base import VectorStoreConfig
from app.entities.dao.model import get_model
from app.entities.dao.vector_store import get_vector_store
from app.entities.user import User


def check_llm_model_config(
        session: Session, llm_model_config: LlmModelConfig,
        current_user: User):
    model_id = llm_model_config.model_id
    model_entity = get_model(session, model_id, current_user.tenant_id)
    if not model_entity:
        raise BizException.create(ErrorCode.model_id_not_found, id=model_id)
    elif model_entity.type != ModelType.LLM:
        raise BizException.create(
            ErrorCode.model_not_llm, model_type=model_entity.type.name)


def check_embedding_model_config(
        session: Session, embedding_model_config: EmbeddingModelConfig,
        current_user: User):
    if embedding_model_config.model_id:
        model_id = embedding_model_config.model_id
        model_entity = get_model(session, model_id, current_user.tenant_id)
        if not model_entity:
            raise BizException.create(ErrorCode.model_id_not_found, id=model_id)
        elif model_entity.type != ModelType.TextEmbedding:
            raise BizException.create(
                ErrorCode.model_not_text_embedding, model_type=model_entity.type.name)
    else:
        # transformer
        model_name = embedding_model_config.model_name
        if not is_valid_model_name(ModelType.TextEmbedding, model_name):
            raise BizException.create(
                ErrorCode.model_name_not_supported,
                model_name=model_name)


def check_vector_store_config(
        session: Session, vector_store_config: VectorStoreConfig,
        current_user: User):
    vector_store_id = vector_store_config.vector_store_id
    vector_store_entity = get_vector_store(
        session, vector_store_id, current_user.tenant_id)
    if not vector_store_entity:
        raise BizException.create(
            ErrorCode.vector_store_id_not_found, id=vector_store_id)


def check_retrieval_model_config(
        session: Session, retrieval_model_config: RetrievalModelConfig,
        current_user: User):
    reranking_model_id = retrieval_model_config.reranking_model_id
    model_entity = get_model(session, reranking_model_id, current_user.tenant_id)
    if not model_entity:
        raise BizException.create(ErrorCode.model_id_not_found, id=reranking_model_id)
