from typing import Type

from langchain_core.vectorstores import VectorStore
from langchain_postgres import PGEngine, PGVectorStore
from pydantic import BaseModel, PositiveInt
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.inspection import inspect

from app.core.vector_store.provider.base import VectorProvider


class PostgresVectorStoreConfig(BaseModel):
    url: str  # postgresql+psycopg://user:password@host:port/database
    pool_size: PositiveInt | None = None
    pool_timeout: PositiveInt | None = None


class PostgresVectorProvider(
    VectorProvider[PostgresVectorStoreConfig, PGEngine]):

    @staticmethod
    def get_config_type() -> Type[PostgresVectorStoreConfig]:
        return PostgresVectorStoreConfig

    def _create_client(self) -> PGEngine:
        optional_params = {
            "pool_size": self.config.pool_size,
            "pool_timeout": self.config.pool_timeout,
        }
        optional_params = {k: v for k, v in optional_params.items() if v}
        # engine = create_async_engine(settings.PGVECTOR_URL, **optional_params)

        # PGEngine.from_engine(engine)
        return PGEngine.from_connection_string(
            url=self.config.url, **optional_params)

    def _create_vector_store(self) -> VectorStore:
        self.create_collection_if_absent()

        return PGVectorStore.create_sync(
            engine=self.client,
            table_name=self.collection_name,
            embedding_service=self.model_provider.model,
            id_column="id", metadata_json_column="metadata"
        )

    def create_collection_if_absent(self):
        try:
            self.client.init_vectorstore_table(
                self.collection_name,
                2560,
                id_column="id", metadata_json_column="metadata")
        except ProgrammingError as e:
            if "already exists" not in str(e):
                raise e

    def has_collection(self, collection_name: str):
        with self.client._pool.connect() as conn:
            return inspect(conn).has_table(collection_name)
