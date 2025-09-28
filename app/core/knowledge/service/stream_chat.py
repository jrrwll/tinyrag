from typing import AsyncIterable, Iterable

from sqlmodel import Session

from app.common.error_code import BizException, ErrorCode
from app.core.knowledge.api import KnowledgeChat, KnowledgePublic, \
    KnowledgeStreamChatPublic
from app.core.model.llm.base import get_llm_provider
from app.core.vector_store.provider.base import VectorProviderFactory
from app.entities.dao.knowledge import get_knowledge, get_knowledge_conversation
from app.entities.knowledge import Knowledge, KnowledgeConversation
from app.entities.repo.model import get_embedding_model_from_config, \
    get_llm_model_from_config
from app.entities.repo.vector_store import get_vector_store_from_config
from app.entities.user import User


async def stream_chat_knowledge(
        session: Session, params: KnowledgeChat, current_user: User
) -> AsyncIterable[str]:
    tenant_id = current_user.tenant_id
    conversation_id, query = params.conversation_id, params.query

    entity = get_knowledge_conversation(
        session, conversation_id, tenant_id)
    if not entity:
        raise BizException.create(ErrorCode.knowledge_conversation_not_found)

    knowledge_id = entity.knowledge_id
    knowledge_entity = get_knowledge(session, knowledge_id, tenant_id)
    if not knowledge_entity:
        raise BizException.create(
            ErrorCode.knowledge_id_not_found, id=knowledge_id)
    knowledge = KnowledgePublic.create(knowledge_entity)

    collection_name = Knowledge.get_collection_name(knowledge.id)
    vector_store = get_vector_store_from_config(
        session, knowledge.vector_store_config, tenant_id)
    embedding_model = get_embedding_model_from_config(
        session, knowledge.embedding_model_config, tenant_id)
    vector_provider = VectorProviderFactory.create_vector(
        collection_name, vector_store, embedding_model)

    search_kwargs = {}
    retrieval_model_config = knowledge.retrieval_model_config
    if retrieval_model_config:
        if retrieval_model_config.top_k is not None:
            search_kwargs["k"] = retrieval_model_config.top_k
    docs = vector_provider.similarity_search(query, **search_kwargs)

    llm_model = get_llm_model_from_config(session, knowledge.llm_model_config, tenant_id)
    llm_provider = get_llm_provider(llm_model)

    print(f"docs:\n{docs}")
    prompt = f"""
    请根据搜索到的文档回答用户的提问

    用户的提问：###{query}###
    
    搜索到的文档：
    {"\n".join([doc.content for doc in docs])}
    """
    print(prompt)

    full_response = []
    async for chunk in llm_provider.arun(prompt):
        full_response.append(chunk)
        yield chunk
    print(f"full_response:\n{full_response}")

    # return llm_provider.arun(prompt)


def stream_chat_knowledge2(
        session: Session, params: KnowledgeChat, current_user: User
) -> KnowledgeStreamChatPublic:
    conversation_id = params.conversation_id
    entity = session.get(KnowledgeConversation, conversation_id)
    if not entity:
        raise BizException.create(ErrorCode.knowledge_conversation_not_found)

    knowledge_id = entity.knowledge_id
    knowledge_entity = session.get(Knowledge, knowledge_id)
    if not knowledge_entity:
        raise BizException.create(ErrorCode.knowledge_id_not_found, id=knowledge_id)

    raise NotImplementedError()

