from functools import cache

from langchain_chroma import Chroma
from langchain_core.vectorstores import VectorStore
from langchain_milvus import Milvus
from langchain_postgres import PGEngine, PGVectorStore
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from app.common.error_code import BizException, ErrorCode
from app.config import settings
from app.core.dataset.enums import VectorStoreType
from app.core.model.default_model import get_default_model_provider
from app.core.model.enums import ModelType
from langchain_core.embeddings import Embeddings

@cache
def get_vector_store() -> VectorStore:
    model_provider = get_default_model_provider(ModelType.TextEmbedding)
    if not model_provider:
        raise BizException.new(ErrorCode.default_model_not_set, ModelType.TextEmbedding)
    embeddings = model_provider.embeddings_model

    typ = settings.VECTOR_STORE_TYPE
    if typ == VectorStoreType.Qdrant:
        return create_qdrant_vector_store(embeddings)
    elif typ == VectorStoreType.PGVector:
        return create_pg_vector_store(embeddings)
    elif typ == VectorStoreType.Milvus:
        return create_milvus_vector_store(embeddings)
    else:
        return create_chroma_vector_store(embeddings)


def create_chroma_vector_store(embeddings: Embeddings) -> VectorStore:
    return Chroma(
        collection_name=settings.VECTOR_STORE_COLLECTION_NAME,
        persist_directory=settings.vector_store__persist_directory,
        embedding_function=embeddings,
    )

def create_qdrant_vector_store(embeddings: Embeddings) -> VectorStore:
    client = QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY,
    )

    return QdrantVectorStore(
        client,
        collection_name=settings.VECTOR_STORE_COLLECTION_NAME,
        embedding=embeddings,
    )


def create_pg_vector_store(embeddings: Embeddings) -> VectorStore:
    engine = PGEngine.from_connection_string(url=settings.PGVECTOR_URL)

    return PGVectorStore.create_sync(
        engine=engine,
        table_name=settings.VECTOR_STORE_COLLECTION_NAME,
        embedding_service=embeddings,
    )

def create_milvus_vector_store(embeddings: Embeddings) -> VectorStore:
    return Milvus(
        collection_name=settings.VECTOR_STORE_COLLECTION_NAME,
        connection_args={
            "uri": settings.MILVUS_URL,
            "user": settings.MILVUS_USER,
            "password": settings.MILVUS_PASSWORD,
            "db_name": settings.MILVUS_DB_NAME,
            "token": settings.MILVUS_TOKEN,
            "timeout": settings.MILVUS_TIMEOUT
        },
        embedding_function=embeddings
    )
