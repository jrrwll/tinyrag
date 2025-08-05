from typing import Type

from langchain_core.embeddings import Embeddings
from langchain_ollama import OllamaEmbeddings
from pydantic import BaseModel
from app.core.model.embedding.base import EmbeddingProvider


class OllamaEmbeddingConfig(BaseModel):
    vector_size: int | None = None
    base_url: str | None = None
    api_key: str | None = None
    content_length: int = 4096
    timeout: int | None = None


class OllamaEmbeddingProvider(EmbeddingProvider[OllamaEmbeddingConfig]):

    @staticmethod
    def get_provider_name() -> str:
        return "ollama"

    @staticmethod
    def get_config_type() -> Type[OllamaEmbeddingConfig]:
        return OllamaEmbeddingConfig

    def _create_model(self) -> Embeddings:
        model_name = self.model_name
        base_url = self.model_config.base_url

        return OllamaEmbeddings(
            base_url=base_url, model=model_name,
            client_kwargs=self._create_client_kwargs())

    def _create_client_kwargs(self) -> dict:  # type: ignore[type-arg]
        client_kwargs = {}
        if self.model_config.timeout:
            client_kwargs["timeout"] = self.model_config.timeout
        return client_kwargs
