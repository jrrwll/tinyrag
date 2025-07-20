from enum import StrEnum


class DatasetType(StrEnum):
    Upload = "upload"
    WebSite = "website"


class VectorStoreType(StrEnum):
    Chroma = "chroma"
    Qdrant = "qdrant"
    PGVector = "pgvector"
    Milvus = "milvus"
