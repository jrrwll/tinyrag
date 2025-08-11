from abc import ABC
from typing import Any, MutableMapping

from cachetools import TTLCache
from langchain_core.embeddings import Embeddings
from pydantic import BaseModel, Field, PositiveInt

from app.core.model.api import ModelPublic
from app.core.model.enums import ModelType
from app.core.model.provider import ModelProvider, ModelProviderFactory

_model_cache: TTLCache[str, Embeddings] = TTLCache(
    maxsize=1000, ttl=10 * 60)  # 10min


class BaseEmbeddingConfig(BaseModel):
    vector_size: PositiveInt | None = Field(
        default=None, json_schema_extra={"builtin": True})


class EmbeddingProvider[T: BaseEmbeddingConfig](ModelProvider[T, Embeddings], ABC):

    @staticmethod
    def get_model_type() -> ModelType:
        return ModelType.TextEmbedding

    @staticmethod
    def _model_cache() -> MutableMapping[str, Embeddings]:
        return _model_cache

    def embed_query(self, text: str) -> list[float]:
        return self.model.embed_query(text)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.model.embed_documents(texts)


def get_embedding_provider(model: ModelPublic) -> EmbeddingProvider[Any]:
    provider_name = model.provider_name
    cls = ModelProviderFactory.get_provider_class(
        ModelType.TextEmbedding, provider_name)
    return cls(model)
