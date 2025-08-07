from typing import Type

from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings
from pydantic import PositiveFloat

from app.core.model.embedding.base import BaseEmbeddingConfig, EmbeddingProvider


class OpenaiEmbeddingConfig(BaseEmbeddingConfig):
    api_key: str
    timeout: PositiveFloat | None = None


class OpenAILLMProvider(EmbeddingProvider[OpenaiEmbeddingConfig]):

    @staticmethod
    def get_provider_name() -> str:
        return "openai"

    @staticmethod
    def get_config_type() -> Type[OpenaiEmbeddingConfig]:
        return OpenaiEmbeddingConfig

    def _create_model(self) -> Embeddings:
        model_name = self.model_name

        api_key = self.model_config.api_key

        timeout = None
        if self.model_config.timeout:
            timeout = self.model_config.timeout

        return OpenAIEmbeddings(
            model=model_name,
            api_key=api_key,  # type: ignore[arg-type]
            timeout=timeout,
        )
