from typing import Type

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_ollama import ChatOllama, OllamaEmbeddings

from app.core.model.privoder.base import BaseModelConfig, ModelProvider


class OllamaModelConfig(BaseModelConfig):
    content_length: int = 4096
    max_tokens: int = 4096
    function_calling: bool = False


class OllamaModelProvider(ModelProvider[OllamaModelConfig]):

    @staticmethod
    def get_provider_name() -> str:
        return "ollama"

    @staticmethod
    def get_config_type() -> Type[OllamaModelConfig]:
        return OllamaModelConfig

    def _create_chat_model(self) -> BaseChatModel:
        model_name = self.model_name
        base_url = self.model_config.base_url

        return ChatOllama(
            base_url=base_url, model=model_name,
            client_kwargs=self._create_client_kwargs())

    def _create_text_embedding(self) -> Embeddings:
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
