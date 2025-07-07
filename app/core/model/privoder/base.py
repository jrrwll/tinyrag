from abc import ABCMeta, abstractmethod
from functools import cached_property, lru_cache
from typing import Type

from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel

from app.common.config import settings
from app.common.error_code import BizException, ErrorCode
from app.core.model.api import ModelPublic
from app.core.model.base import LLMPrompt, ModelParams
from app.core.model.service import process_model_config, process_prompt
from app.core.variable.base import Variable
from app.util.langchain.callbacks import CompleteResponseHandler
from langchain_core.messages import BaseMessage


class ModelProviderRegistry(ABCMeta):

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        if not hasattr(cls, "implements"):
            cls.implements = []
        else:
            cls.implements.append(cls)


class ModelProvider(metaclass=ModelProviderRegistry):
    model: ModelPublic

    def __init__(self, model: ModelPublic):
        self.model = model

    @staticmethod
    @abstractmethod
    def get_provider_name() -> str:
        pass

    @cached_property
    def chat_model(self) -> BaseChatModel:
        return self._create_chat_model()

    @abstractmethod
    def _create_chat_model(self) -> BaseChatModel:
        pass

    def test_run(self,
            prompt: str | None = None) -> dict:  # type: ignore[type-arg]
        if not prompt:
            prompt = settings.DEFAULT_TEST_PROMPT

        msg = self.chat_model.invoke(prompt)
        return msg.model_dump()

    def run(self, model_params: ModelParams,
            messages: list[BaseMessage]) -> str:
        model_config = process_model_config(model_params)

        response = self.chat_model.invoke(messages, config=model_config)
        return response.content

    def run_structured_output(self, model_params: ModelParams,
            messages: list[BaseMessage],
            structured_output_type: Type[BaseModel]) -> list[Variable]:
        model_config = process_model_config(model_params)

        structured_chat = self.chat_model.with_structured_output(
            structured_output_type)

        handler = CompleteResponseHandler()
        model_config["callbacks"] = [handler]
        structured_output = structured_chat.invoke(
            messages, config=model_config)

        return [Variable(name=name, value=value) for name, value
                in dict(structured_output).items()]


@lru_cache(maxsize=1000)
def get_model_provider(model: ModelPublic) -> ModelProvider:
    provider_name = model.provider_name
    for cls in ModelProvider.implements:
        if cls.get_provider_name() == provider_name:
            return cls(model)

    raise BizException.new(ErrorCode.model_provider_not_supported, provider_name)
