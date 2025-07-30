from chromadb import Client, DEFAULT_DATABASE, DEFAULT_TENANT, HttpClient
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_core.vectorstores import VectorStore

from app.config import settings
from app.core.rag.vector.vectorstores import BaseVectorStore


class ChromaVector(BaseVectorStore):

    client: Client
    vector_store: Chroma

    def _init(self) -> None:
        if not settings.CHROMA_HOST:
            persist_directory = settings.CHROMA_PERSIST_DIRECTORY
            if not persist_directory:
                persist_directory = settings.vector_store_persist_directory

            self.vector_store = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.model_provider.model,
                persist_directory=persist_directory,
            )
            self.client = self.vector_store._client
        else:
            self.client = HttpClient(
                host=settings.CHROMA_HOST,
                port=settings.CHROMA_PORT,
                tenant=settings.CHROMA_TENANT or DEFAULT_TENANT,
                database=settings.CHROMA_DATABASE or DEFAULT_DATABASE,
                settings = Settings(
                    chroma_client_auth_provider=settings.CHROMA_AUTH_PROVIDERS,
                    chroma_client_auth_credentials=settings.CHROMA_AUTH_CREDENTIALS,
                )
            )
            self.vector_store = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.model_provider.model,
                client=self.client,
            )

        # self.vector_store._client.get_or_create_collection(self.collection_name)

    def get_vector_store(self) -> VectorStore:
        return self.vector_store
