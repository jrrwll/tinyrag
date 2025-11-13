import asyncio
import logging
from abc import ABC
from typing import Any, Iterable, AsyncIterable, MutableMapping, Type

from cachetools import TTLCache
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from pydantic import BaseModel

from app.config import settings
from app.core.model.api import ModelChatResult, ModelPublic
from app.core.model.base import ModelParams
from app.core.model.enums import ModelType
from app.core.model.provider import ModelProvider, ModelProviderFactory
from app.core.variable.base import Variable
from corepy.net.sse import sse_format
from app.util.langchain.callbacks import CompleteResponseHandler

logger = logging.getLogger(__name__)


class BaseModelConfig(BaseModel):
    timeout: int | None = None


class LLMProvider[T: BaseModelConfig](ModelProvider[T, BaseChatModel], ABC):

    @staticmethod
    def get_model_type() -> ModelType:
        return ModelType.LLM

    @staticmethod
    def _model_cache() -> MutableMapping[str, BaseChatModel]:
        return _model_cache

    def test_run(self,
            prompt: str | None = None
    ) -> dict:  # type: ignore[type-arg]
        if not prompt:
            prompt = settings.DEFAULT_TEST_PROMPT

        logger.info(f"Test run with prompt: {prompt}")
        msg = self.model.invoke(prompt)
        return msg.model_dump()

    async def arun(self,
            prompt: str | None = None
    ) -> AsyncIterable[str]:  # type: ignore[type-arg]
        if not prompt:
            prompt = settings.DEFAULT_TEST_PROMPT

        logger.info(f"Test run with prompt: {prompt}")
        async for chunk in self.model.astream(prompt):
            if not chunk.content:
                continue
            yield await sse_format(ModelChatResult(
                token=chunk.content,
            ))

            # rate limiting
            await asyncio.sleep(0.01)

        yield await sse_format(ModelChatResult(done=True))

    def run(self, model_params: ModelParams,
            messages: list[BaseMessage]) -> str:
        model_config = _process_model_config(model_params)

        response = self.model.invoke(messages, config=model_config)
        return response.content

    def run_structured_output(self, model_params: ModelParams,
            messages: list[BaseMessage],
            structured_output_type: Type[BaseModel]) -> list[Variable]:
        model_config = _process_model_config(model_params)

        structured_chat = self.model.with_structured_output(
            structured_output_type)

        handler = CompleteResponseHandler()
        model_config["callbacks"] = [handler]
        structured_output = structured_chat.invoke(
            messages, config=model_config)

        return [Variable(name=name, value=value) for name, value
                in dict(structured_output).items()]


_model_cache: TTLCache[str, BaseChatModel] = TTLCache(
    maxsize=1000, ttl=10 * 60)  # 10min


def get_llm_provider(model: ModelPublic) -> LLMProvider[Any]:
    provider_name = model.provider_name
    cls = ModelProviderFactory.get_provider_class(ModelType.LLM, provider_name)
    return cls(model)


def _process_model_config(params: ModelParams):
    return {}
