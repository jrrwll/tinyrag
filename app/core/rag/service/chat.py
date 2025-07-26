from app.common.db import open_session
from app.core.model.privoder.base import get_model_provider
from app.core.rag.api import DatasetChat, DatasetChatPublic
from app.entities.dataset import Dataset, DatasetConversation
from app.entities.workflow_run import Conversation


def chat_dataset(entity: Conversation, dataset_entity: Dataset) -> DatasetChatPublic:
    pass


def ass():
    from langgraph.graph import START, MessagesState, StateGraph
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.checkpoint.postgres import PostgresSaver

    workflow = StateGraph(state_schema=MessagesState)

    memory = MemorySaver()
    memory = PostgresSaver.from_conn_string("")

    app = workflow.compile(checkpointer=memory)
