from langchain_core.vectorstores import VectorStore
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from app.config import settings
from app.core.model.privoder import ModelProvider
from app.core.model.privoder.base import get_model_provider
from app.core.rag.vector.vectorstores import BaseVectorStore
from app.entities.model import Model


class QdrantVector(BaseVectorStore):

    model_provider: ModelProvider

    client: QdrantClient
    vector_store: QdrantVectorStore

    def __init__(self, collection_name: str, model: Model):
        super().__init__(collection_name)

        self.model_provider = get_model_provider(model)

        if not settings.QDRANT_URL:
            local_path = settings.QDRANT_LOCAL_PATH
            if not local_path:
                local_path = settings.vector_store_persist_directory

            self.client = QdrantClient(path=local_path)
        else:
            optional_params = {
                "port": settings.QDRANT_PORT,
                "grpc_port": settings.QDRANT_GRPC_PORT,
                "https": settings.QDRANT_HTTPS,
            }
            optional_params = {k: v for k, v in optional_params.items() if v}

            self.client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY,
                prefer_grpc=settings.QDRANT_GRPC_ENABLED,
                **optional_params
            )

        self.vector_store = QdrantVectorStore(
            self.client,
            collection_name=self.collection_name,
            embedding=self.model_provider.embeddings_model,
        )

        self.client.create_collection(self.collection_name)

    def get_vector_store(self) -> VectorStore:
        return self.vector_store
