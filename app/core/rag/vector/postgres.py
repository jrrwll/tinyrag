from langchain_core.vectorstores import VectorStore
from langchain_postgres import PGEngine, PGVectorStore
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings
from app.core.model.privoder.base import ModelProvider, get_model_provider
from app.core.rag.vector.vectorstores import BaseVectorStore
from app.entities.model import Model


class PostgresVector(BaseVectorStore):
    model_provider: ModelProvider

    pg_engine: PGEngine
    vector_store: PGVectorStore

    def __init__(self, collection_name: str, model: Model):
        super().__init__(collection_name)

        self.model_provider = get_model_provider(model)

        optional_params = {
            "pool_size": settings.PGVECTOR_POOL_SIZE,
            "pool_timeout": settings.PGVECTOR_POOL_TIMEOUT,
        }
        optional_params = {k: v for k, v in optional_params.items() if v}
        engine = create_async_engine(settings.PGVECTOR_URL, **optional_params)

        self.pg_engine = PGEngine.from_engine(engine)

        self.vector_store = PGVectorStore.create_sync(
            engine=self.pg_engine,
            table_name=collection_name,
            embedding_service=self.model_provider.embeddings_model,
        )

    def get_vector_store(self) -> VectorStore:
        return self.vector_store
