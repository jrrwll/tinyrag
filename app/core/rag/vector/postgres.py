from langchain_core.vectorstores import VectorStore
from langchain_postgres import PGEngine, PGVectorStore
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.inspection import inspect

from app.config import settings
from app.core.rag.vector.vectorstores import BaseVectorStore


class PostgresVector(BaseVectorStore):

    pg_engine: PGEngine
    vector_store: PGVectorStore

    def _init(self) -> None:
        optional_params = {
            "pool_size": settings.PGVECTOR_POOL_SIZE,
            "pool_timeout": settings.PGVECTOR_POOL_TIMEOUT,
        }
        optional_params = {k: v for k, v in optional_params.items() if v}
        # engine = create_async_engine(settings.PGVECTOR_URL, **optional_params)

        self.pg_engine = PGEngine.from_connection_string(
            url=settings.PGVECTOR_URL, **optional_params)
        # self.pg_engine = PGEngine.from_engine(engine)

        try:
            self.pg_engine.init_vectorstore_table(
                self.collection_name,
                2560,
                id_column="id", metadata_json_column="metadata")
        except ProgrammingError as e:
            if "already exists" not in str(e):
                raise e

        self.vector_store = PGVectorStore.create_sync(
            engine=self.pg_engine,
            table_name=self.collection_name,
            embedding_service=self.model_provider.model,
            id_column="id", metadata_json_column="metadata"
        )

    def get_vector_store(self) -> VectorStore:
        return self.vector_store

    def has_collection(self, collection_name: str):
        with self.pg_engine._pool.connect() as conn:
            return inspect(conn).has_table(collection_name)
