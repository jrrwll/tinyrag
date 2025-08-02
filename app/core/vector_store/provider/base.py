import threading
from abc import ABC, abstractmethod
from typing import Any, Iterable, Type

from cachetools import TTLCache
from pydantic import BaseModel

from app.core.knowledge.text_process.base import DocumentModel
from app.core.model.api import ModelPublic
from app.core.model.embedding.base import EmbeddingProvider, \
    get_embedding_provider
from app.core.vector_store.api import VectorStorePublic
from app.core.vector_store.enums import VectorStoreType
from langchain_core.vectorstores import VectorStore

_client_cache: TTLCache[str, Any] = TTLCache(
    maxsize=1000, ttl=10 * 60)  # 10 min


class VectorProvider[Cfg: BaseModel, C](ABC):

    _lock = threading.Lock()

    @staticmethod
    @abstractmethod
    def _get_config_type() -> Type[Cfg]:
        raise NotImplementedError()

    def _create_client(self) -> C:
        raise NotImplementedError()

    def _create_vector_store(self) -> VectorStore:
        raise NotImplementedError()

    def __init__(self, collection_name: str, vector_store: VectorStorePublic,
            model: ModelPublic):
        self.collection_name: str = collection_name
        self.model_provider: EmbeddingProvider = get_embedding_provider(model)
        self._footprint = f"{model.footprint()}:{vector_store.footprint()}"
        self.config: Cfg = self._get_config_type()(**vector_store.config)
        self.vector_store_local_dir = vector_store.local_dir()
        self._init()

    def _init(self) -> None:
        with self._lock:
            client = _client_cache.get(self._footprint)
            if client:
                self.client = client
                # renewal ttl
                _client_cache[self._footprint] = client
            else:
                self.client = self._create_client()
                _client_cache[self._footprint] = self.client

        self.vector_store = self._create_vector_store()

    def add_documents(self, documents: Iterable[DocumentModel]) -> None:
        docs = [d.to_document() for d in documents]
        self.vector_store.add_documents(docs)

    def add_texts(self, documents: Iterable[DocumentModel]):
        ids, texts, metadatas = [], [], []
        for d in documents:
            ids.append(d.id)
            texts.append(d.content)
            metadatas.append(d.metadata)

        self.vector_store.add_texts(ids=ids, texts=texts, metadatas=metadatas)

    def similarity_search(self, query: str, k: int = 4) -> list[DocumentModel]:
        docs = self.vector_store.similarity_search(query, k)
        return [DocumentModel.create(doc) for doc in docs]


class VectorProvideFactory:

    @staticmethod
    def create_vector(
            collection_name: str, vector_store: VectorStorePublic,
            model: ModelPublic
    ) -> VectorProvider:
        vector_class = VectorProvideFactory._get_vector_class(
            vector_store.type)

        return vector_class(collection_name, vector_store, model)

    @staticmethod
    def _get_vector_class[T: VectorProvider](
            vector_store_type: VectorStoreType) -> Type[T]:
        if vector_store_type == VectorStoreType.Qdrant:
            from app.core.vector_store.provider.qdrant import \
                QdrantVectorProvider

            return QdrantVectorProvider
        elif vector_store_type == VectorStoreType.PGVector:
            from app.core.vector_store.provider.postgres import \
                PostgresVectorProvider

            return PostgresVectorProvider
        elif vector_store_type == VectorStoreType.Milvus:
            from app.core.vector_store.provider.milvus import \
                MilvusVectorProvider

            return MilvusVectorProvider
        elif vector_store_type == VectorStoreType.LanceDB:
            from app.core.vector_store.provider.lancedb import \
                LanceDBVectorProvider

            return LanceDBVectorProvider
        else:
            from app.core.vector_store.provider.chroma import \
                ChromaVectorProvider

            return ChromaVectorProvider
