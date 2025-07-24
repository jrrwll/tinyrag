from typing import Type

from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from app.core.model.privoder.base import BaseModelConfig, ModelProvider


class OpenaiModelConfig(BaseModelConfig):
    max_tokens: int | None = None


class OpenAIModelProvider(ModelProvider[OpenaiModelConfig]):
    @staticmethod
    def get_provider_name() -> str:
        return "openai"

    @staticmethod
    def get_config_type() -> Type[OpenaiModelConfig]:
        return OpenaiModelConfig

    def _create_chat_model(self) -> BaseChatModel:
        model_name = self.model_name

        base_url = self.model_config.base_url
        api_key = self.model_config.api_key

        timeout = None
        if self.model_config.timeout:
            timeout = float(self.model_config.timeout)

        return ChatOpenAI(
            base_url=base_url,
            model=model_name,
            api_key=api_key,  # type: ignore[arg-type]
            max_tokens=self.model_config.max_tokens,
            timeout=timeout,
        )

    def _create_text_embedding(self) -> Embeddings:
        model_name = self.model_name

        base_url = self.model_config.base_url
        api_key = self.model_config.api_key

        timeout = None
        if self.model_config.timeout:
            timeout = float(self.model_config.timeout)

        return OpenAIEmbeddings(
            base_url=base_url,
            model=model_name,
            api_key=api_key,  # type: ignore[arg-type]
            timeout=timeout,
        )
