from cachetools import TTLCache
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore

from app.common.error_code import BizException, ErrorCode
from app.config import settings
from app.core.rag.enums import VectorStoreType
from app.core.model.default_model import get_default_model_provider
from app.core.model.enums import ModelType

# TODO broadcast to clear caches
_cache: TTLCache[VectorStoreType, VectorStore] = TTLCache(maxsize=1, ttl=10 * 60) # 10min

def create_vector_store(collection_name: str) -> VectorStore:
    typ = settings.VECTOR_STORE_TYPE

    vector_store = _cache.get(typ)
    if vector_store:
        return vector_store

    model_provider = get_default_model_provider(ModelType.TextEmbedding)
    if not model_provider:
        raise BizException.new(ErrorCode.default_model_not_set, ModelType.TextEmbedding)
    embeddings = model_provider.embeddings_model

    if typ == VectorStoreType.Qdrant:
        vector_store = _create_qdrant_vector_store(embeddings)
    elif typ == VectorStoreType.PGVector:
        vector_store = _create_pg_vector_store(embeddings)
    elif typ == VectorStoreType.Milvus:
        vector_store = _create_milvus_vector_store(embeddings)
    else:
        vector_store = _create_chroma_vector_store(embeddings)
    _cache[typ] = vector_store
    return _cache[typ]


def _create_chroma_vector_store(embeddings: Embeddings) -> VectorStore:
    from langchain_chroma import Chroma

    return Chroma(
        collection_name=settings.VECTOR_STORE_COLLECTION_NAME,
        persist_directory=settings.vector_store_persist_directory,
        embedding_function=embeddings,
    )

def _create_qdrant_vector_store(embeddings: Embeddings) -> VectorStore:
    from langchain_qdrant import QdrantVectorStore
    from qdrant_client import QdrantClient

    client = QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY,
    )

    return QdrantVectorStore(
        client,
        collection_name=settings.VECTOR_STORE_COLLECTION_NAME,
        embedding=embeddings,
    )


def _create_pg_vector_store(embeddings: Embeddings) -> VectorStore:
    from langchain_postgres import PGEngine, PGVectorStore

    engine = PGEngine.from_connection_string(url=settings.PGVECTOR_URL)

    return PGVectorStore.create_sync(
        engine=engine,
        table_name=settings.VECTOR_STORE_COLLECTION_NAME,
        embedding_service=embeddings,
    )

def _create_milvus_vector_store(embeddings: Embeddings) -> VectorStore:
    from langchain_milvus import Milvus

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
