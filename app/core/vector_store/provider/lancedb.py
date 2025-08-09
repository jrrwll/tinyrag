from datetime import timedelta
from typing import Any, Type

from chromadb import ClientAPI
from lancedb import DBConnection, connect
from langchain_community.vectorstores import LanceDB
from langchain_core.vectorstores import VectorStore
from pydantic import BaseModel

from app.core.vector_store.provider.base import VectorProvider


class LanceDBVectorStoreConfig(BaseModel):
    uri: str
    api_key: str | None = None
    region: str | None = None
    host_override: str | None = None
    read_consistency_interval: timedelta | None = None

    client_config: dict[str, Any] | None = None
    storage_options: dict[str, str] | None = None


class LanceDBVectorProvider(
    VectorProvider[LanceDBVectorStoreConfig, ClientAPI]):

    @staticmethod
    def get_config_type() -> type[LanceDBVectorStoreConfig]:
        return LanceDBVectorStoreConfig

    def _create_client(self) -> DBConnection:
        kwargs = self.config.model_dump(exclude_none=True)
        return connect(**kwargs)

    def _create_vector_store(self) -> VectorStore:
        return LanceDB(
            connection=self.client,
            embedding=self.model_provider.model,
            table_name=self.collection_name,
        )
