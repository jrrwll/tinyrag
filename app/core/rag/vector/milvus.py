from langchain_core.vectorstores import VectorStore
from langchain_milvus import Milvus


from app.config import settings
from app.core.model.privoder.base import ModelProvider, get_model_provider
from app.core.rag.vector.vectorstores import BaseVectorStore
from app.entities.model import Model
from pymilvus import MilvusClient


class MilvusVector(BaseVectorStore):

    model_provider: ModelProvider

    client: MilvusClient
    vector_store: Milvus

    def __init__(self, collection_name: str, model: Model):
        super().__init__(collection_name)

        self.model_provider = get_model_provider(model)

        connection_args={
            "uri": settings.MILVUS_URL,
            "user": settings.MILVUS_USER,
            "password": settings.MILVUS_PASSWORD,
            "db_name": settings.MILVUS_DB_NAME,
            "token": settings.MILVUS_TOKEN,
            "timeout": settings.MILVUS_TIMEOUT
        }
        connection_args = {k: v for k, v in connection_args.items() if v}
        self.vector_store = Milvus(
            connection_args=connection_args,
            collection_name=self.collection_name,
            embedding_function=self.model_provider.embeddings_model
        )
        self.client = self.vector_store._milvus_client

    def get_vector_store(self) -> VectorStore:
        return self.vector_store
