from app.common.error_code import BizException, ErrorCode
from app.core.knowledge.api import KnowledgeChat, KnowledgeChatPublic
from app.entities.knowledge import Knowledge
from app.entities.knowledge import KnowledgeConversation
from app.entities.user import User
from sqlmodel import Session


def chat_knowledge(
        session: Session, params: KnowledgeChat, current_user: User
) -> KnowledgeChatPublic:
    conversation_id = params.conversation_id
    entity = session.get(KnowledgeConversation, conversation_id)
    if not entity:
        raise BizException.create(ErrorCode.knowledge_conversation_not_found, id)

    knowledge_id = entity.knowledge_id
    knowledge_entity = session.get(Knowledge, knowledge_id)
    if not knowledge_entity:
        raise BizException.create(ErrorCode.knowledge_not_found, id)

    raise NotImplementedError()


def ass():
    from langgraph.graph import MessagesState, StateGraph
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.checkpoint.postgres import PostgresSaver

    workflow = StateGraph(state_schema=MessagesState)

    memory = MemorySaver()
    memory = PostgresSaver.from_conn_string("")

    app = workflow.compile(checkpointer=memory)
