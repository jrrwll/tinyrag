import logging
from typing import Iterable, Type

from langchain_core.vectorstores import VectorStore
from langchain_qdrant import QdrantVectorStore
from pydantic import BaseModel, PositiveInt
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from app.core.knowledge.text_process.base import DocumentModel
from app.core.vector_store.provider.base import VectorProvider

logger = logging.getLogger(__name__)


class QdrantVectorStoreConfig(BaseModel):
    url: str
    port: PositiveInt | None = None
    grpc_port: PositiveInt | None = None
    prefer_grpc: bool = False

    api_key: str | None = None
    https: bool | None = None
    timeout: int | None = None


class QdrantVectorProvider(
    VectorProvider[QdrantVectorStoreConfig, QdrantClient]):

    @staticmethod
    def get_config_type() -> Type[QdrantVectorStoreConfig]:
        return QdrantVectorStoreConfig

    def _create_client(self) -> QdrantClient:
        if self.config.url == '*':
            return QdrantClient(path=self.vector_store_local_dir)

        kwargs = self.config.model_dump(exclude_none=True)
        return QdrantClient(**kwargs)

    def _create_vector_store(self) -> VectorStore:
        return QdrantVectorStore(
            self.client,
            collection_name=self.collection_name,
            embedding=self.model_provider.model,
        )

    def create_collection_if_absent(self):
        # must create collection before using it
        if self.client.collection_exists(self.collection_name):
            return

        vectors_config = VectorParams(
            size=2560,
            distance=Distance.COSINE
        )

        logger.info(f"vector create collection {self.collection_name}")
        self.client.create_collection(self.collection_name,
                                      vectors_config=vectors_config)


    def add_documents(self, documents: Iterable[DocumentModel]) -> None:
        pass
