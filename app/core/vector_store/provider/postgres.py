import asyncio

from langchain_core.vectorstores import VectorStore
from langchain_postgres import PGEngine, PGVectorStore
from pydantic import BaseModel, PositiveInt, SecretStr, PostgresDsn
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.vector_store.provider.base import VectorProvider


class PostgresVectorStoreConfig(BaseModel):
    user: str
    password: SecretStr | None = None
    host: str
    port: PositiveInt | None = None
    database: str
    query: str | None = None

    pool_size: PositiveInt | None = None
    pool_timeout: PositiveInt | None = None


class PostgresVectorProvider(
    VectorProvider[PostgresVectorStoreConfig, PGEngine]):

    @staticmethod
    def get_config_type() -> type[PostgresVectorStoreConfig]:
        return PostgresVectorStoreConfig

    def _create_client(self) -> PGEngine:
        optional_params = {
            "pool_size": self.config.pool_size,
            "pool_timeout": self.config.pool_timeout,
        }
        optional_params = {k: v for k, v in optional_params.items() if v}
        # engine = create_async_engine(settings.PGVECTOR_URL, **optional_params)

        # postgresql+psycopg2://user:password@host:port/database?query
        url  =str(PostgresDsn.build(
            scheme="postgresql+psycopg2",
            username=self.config.user,
            password=self.config.password and self.config.password.get_secret_value(),
            host=self.config.host,
            port=self.config.port,
            path=f"/{self.config.database}",
            query=self.config.query,
        ))
        # PGEngine.from_engine(engine)
        return PGEngine.from_connection_string(
            url=url, **optional_params)

    def _create_vector_store(self) -> VectorStore:
        return PGVectorStore.create_sync(
            engine=self.client,
            table_name=self.collection_name,
            embedding_service=self.model_provider.model,
            id_column="id", metadata_json_column="metadata"
        )

    def create_collection_if_absent(self):
        if self.has_collection_sync():
            return

        try:
            self.client.init_vectorstore_table(
                self.collection_name,
                self.vector_size,
                id_column="id", metadata_json_column="metadata")
        except ProgrammingError as e:
            if "already exists" not in str(e):
                raise e

    def has_collection_sync(self) -> bool:
        return asyncio.run(self.has_collection())

    async def has_collection(self) -> bool:
        pool: AsyncEngine = self.client._pool
        async with pool.connect() as conn:
            row = await conn.scalar(
                text("select 1 from information_schema.tables where table_name = :tbl"),
                {"tbl": self.collection_name},
            )
            return row is not None
