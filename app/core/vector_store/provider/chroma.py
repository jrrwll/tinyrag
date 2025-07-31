from typing import Type

from chromadb import Client, ClientAPI, HttpClient, Settings
from langchain_chroma import Chroma
from langchain_core.vectorstores import VectorStore
from pydantic import BaseModel, PositiveInt
from app.core.vector_store.provider.base import VectorProvider


class ChromaVectorStoreConfig(BaseModel):
    host: str | None = None
    port: PositiveInt | None = None
    tenant: str | None = None
    database: str | None = None
    auth_provider: str | None = None
    auth_credentials: str | None = None


class ChromaVectorProvider(
    VectorProvider[ChromaVectorStoreConfig, ClientAPI]):

    @staticmethod
    def _get_config_type() -> Type[ChromaVectorStoreConfig]:
        return ChromaVectorStoreConfig

    def _create_client(self) -> Client:
        if not self.config.host:
            client_settings = Settings(
                persist_directory=self.vector_store_local_dir)
            client = Client(client_settings)
            return client

        kwargs = {
            "host": self.config.host,
            "port": self.config.port,
            "tenant": self.config.tenant,
            "database": self.config.database,
            "settings": Settings(
                chroma_client_auth_provider=self.config.auth_provider,
                chroma_client_auth_credentials=self.config.auth_credentials,
            ),
        }
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        return HttpClient(**kwargs)

    def _create_vector_store(self) -> VectorStore:
        return Chroma(
            collection_name=self.collection_name,
            embedding_function=self.model_provider.model,
            client=self.client,
        )

        # self.vector_store._client.get_or_create_collection(self.collection_name)
