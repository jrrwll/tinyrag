from enum import StrEnum


class DocumentSourceType(StrEnum):
    Upload = "upload"
    Storage = "storage"
    WebSite = "website"


class VectorStoreType(StrEnum):
    Chroma = "chroma"
    Qdrant = "qdrant"
    PGVector = "pgvector"
    Milvus = "milvus"
