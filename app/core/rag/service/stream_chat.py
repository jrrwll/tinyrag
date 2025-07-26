from app.core.rag.api import DatasetStreamChatPublic
from app.entities.dataset import Dataset
from app.entities.workflow_run import Conversation


def stream_chat_dataset(entity: Conversation,
        dataset_entity: Dataset) -> DatasetStreamChatPublic:
    pass
