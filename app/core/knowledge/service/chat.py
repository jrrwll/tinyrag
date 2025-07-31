from app.core.knowledge.api import KnowledgeChatPublic
from app.entities.knowledge import Knowledge
from app.entities.knowledge import KnowledgeConversation


def chat_knowledge(entity: KnowledgeConversation,
        knowledge_entity: Knowledge) -> KnowledgeChatPublic:
    pass


def ass():
    from langgraph.graph import MessagesState, StateGraph
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.checkpoint.postgres import PostgresSaver

    workflow = StateGraph(state_schema=MessagesState)

    memory = MemorySaver()
    memory = PostgresSaver.from_conn_string("")

    app = workflow.compile(checkpointer=memory)
