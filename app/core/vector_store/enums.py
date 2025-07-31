from enum import StrEnum


class VectorStoreType(StrEnum):
    Chroma = "chroma"
    Qdrant = "qdrant"
    PGVector = "pgvector"
    Milvus = "milvus"
    LanceDB = "lancedb"
