from typing import Type

from langchain_core.language_models import BaseChatModel
from langchain_ollama import ChatOllama

from app.core.model.llm.base import BaseModelConfig, LLMProvider


class OllamaModelConfig(BaseModelConfig):
    base_url: str | None = None
    content_length: int = 4096
    max_tokens: int = 4096
    function_calling: bool = False


class OllamaLLMProvider(LLMProvider[OllamaModelConfig]):

    @staticmethod
    def get_provider_name() -> str:
        return "ollama"

    @staticmethod
    def get_config_type() -> Type[OllamaModelConfig]:
        return OllamaModelConfig

    def _create_model(self) -> BaseChatModel:
        model_name = self.model_name
        base_url = self.config.base_url

        return ChatOllama(
            base_url=base_url, model=model_name,
            client_kwargs=self._create_client_kwargs())

    def _create_client_kwargs(self) -> dict:  # type: ignore[type-arg]
        client_kwargs = {}
        if self.config.timeout:
            client_kwargs["timeout"] = self.config.timeout
        return client_kwargs
