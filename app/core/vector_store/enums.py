from enum import StrEnum


_TRANSFORMER_MODELS = [
    "all-MiniLM-L6-v2",
    "all-MiniLM-L12-v2",
    "nomic-embed-text-v1",
    "multilingual-e5-small"
]


class EmbeddingType(StrEnum):
    Transformer = "transformer" # sentence-transformers
    Custom = "custom"

    @classmethod
    def is_valid_model_name(cls, model_name: str) -> bool:
        return model_name in _TRANSFORMER_MODELS


class VectorStoreType(StrEnum):
    Chroma = "chroma"
    Qdrant = "qdrant"
    PGVector = "pgvector"
    Milvus = "milvus"
