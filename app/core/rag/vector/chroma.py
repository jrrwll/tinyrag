from langchain_chroma import Chroma
from langchain_core.vectorstores import VectorStore

from app.config import settings
from app.core.model.privoder.base import ModelProvider, get_model_provider
from app.core.rag.vector.vectorstores import BaseVectorStore
from app.entities.model import Model
from chromadb.config import Settings
from chromadb import Client, DEFAULT_TENANT, DEFAULT_DATABASE, HttpClient

class ChromaVector(BaseVectorStore):

    model_provider: ModelProvider

    client: Client
    vector_store: Chroma

    def __init__(self, collection_name: str, model: Model):
        super().__init__(collection_name)

        self.model_provider = get_model_provider(model)

        if not settings.CHROMA_HOST:
            persist_directory = settings.CHROMA_PERSIST_DIRECTORY
            if not persist_directory:
                persist_directory = settings.vector_store_persist_directory

            self.vector_store = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.model_provider.embeddings_model,
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
                embedding_function=self.model_provider.embeddings_model,
                client=self.client,
            )

        self.vector_store._client.get_or_create_collection()

    def get_vector_store(self) -> VectorStore:
        return self.vector_store
