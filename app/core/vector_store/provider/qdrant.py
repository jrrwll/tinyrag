import logging
from typing import Type

from langchain_core.vectorstores import VectorStore
from langchain_qdrant import QdrantVectorStore
from pydantic import BaseModel, PositiveInt
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from app.config import settings
from app.core.vector_store.provider.base import VectorProvider

logger = logging.getLogger(__name__)


class QdrantVectorStoreConfig(BaseModel):
    url: str | None = None
    api_key: str | None = None
    https: bool | None = None
    grpc_port: PositiveInt | None = None
    grpc_enabled: bool = False


class QdrantVectorProvider(
    VectorProvider[QdrantVectorStoreConfig, QdrantClient]):

    @staticmethod
    def _get_config_type() -> Type[QdrantVectorStoreConfig]:
        return QdrantVectorStoreConfig

    def _create_client(self) -> QdrantClient:
        if not self.config.url:
            return QdrantClient(path=self.vector_store_local_dir)
        else:
            optional_params = {
                "port": settings.QDRANT_PORT,
                "grpc_port": settings.QDRANT_GRPC_PORT,
                "https": settings.QDRANT_HTTPS,
            }
            optional_params = {k: v for k, v in optional_params.items() if v}

            return QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY,
                prefer_grpc=settings.QDRANT_GRPC_ENABLED,
                **optional_params
            )

    def _create_vector_store(self) -> VectorStore:
        # must create collection before using it
        self.create_collection_if_absent()

        return QdrantVectorStore(
            self.client,
            collection_name=self.collection_name,
            embedding=self.model_provider.model,
        )

    def create_collection_if_absent(self):
        if self.client.collection_exists(self.collection_name):
            return

        vectors_config = VectorParams(
            size=2560,
            distance=Distance.COSINE
        )

        logger.info(f"vector create collection {self.collection_name}")
        self.client.create_collection(self.collection_name,
                                      vectors_config=vectors_config)
