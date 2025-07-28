from typing import Type

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

from app.core.model.llm.base import BaseModelConfig, LLMProvider


class OpenaiModelConfig(BaseModelConfig):
    api_key: str


class OpenAILLMProvider(LLMProvider[OpenaiModelConfig]):

    @staticmethod
    def get_provider_name() -> str:
        return "openai"

    @staticmethod
    def get_config_type() -> Type[OpenaiModelConfig]:
        return OpenaiModelConfig

    def _create_model(self) -> BaseChatModel:
        model_name = self.model_name

        api_key = self.model_config.api_key

        timeout = None
        if self.model_config.timeout:
            timeout = float(self.model_config.timeout)

        return ChatOpenAI(
            model=model_name,
            api_key=api_key,  # type: ignore[arg-type]
            timeout=timeout,
        )
