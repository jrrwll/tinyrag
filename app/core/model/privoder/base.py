import logging
from abc import ABCMeta, abstractmethod
from typing import Callable, MutableMapping, Type

from cachetools import TTLCache
from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from pydantic import BaseModel

from app.common.error_code import BizException, ErrorCode
from app.config import settings
from app.core.model.api import ModelPublic
from app.core.model.base import ModelParams
from app.core.model.service import process_model_config
from app.core.variable.base import Variable
from app.util.codec import md5
from app.util.langchain.callbacks import CompleteResponseHandler

logger = logging.getLogger(__name__)


class BaseModelConfig(BaseModel):
    base_url: str | None = None
    api_key: str | None = None
    timeout: int | None = None


class ModelProviderRegistry(ABCMeta):

    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        if not hasattr(cls, "implements"):
            cls.implements = []
        else:
            cls.implements.append(cls)


class ModelProvider[T: BaseModelConfig](metaclass=ModelProviderRegistry):
    model_name: str
    model_config: T
    _model_footprint: str

    def __init__(self, model: ModelPublic):
        self.model_name = model.model_name
        self.model_config = self.get_config_type().model_validate(model.config)
        self._model_footprint = md5(model.model_dump_json())

    @staticmethod
    @abstractmethod
    def get_provider_name() -> str:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def get_config_type() -> Type[T]:
        raise NotImplementedError

    @abstractmethod
    def _create_chat_model(self) -> BaseChatModel:
        raise NotImplementedError

    @abstractmethod
    def _create_text_embedding(self) -> Embeddings:
        raise NotImplementedError

    def _get_or_create[T](self, cache: MutableMapping[str, T],
            creator: Callable[[], T]) -> T:
        item = cache.get(self._model_footprint)
        if item:
            return item
        item = creator()
        cache[self._model_footprint] = item
        return item

    @property
    def chat_model(self) -> BaseChatModel:
        return self._get_or_create(
            _chat_model_cache, self._create_chat_model)

    @property
    def embeddings_model(self) -> Embeddings:
        return self._get_or_create(
            _embeddings_cache, self._create_text_embedding)

    def test_run(self,
            prompt: str | None = None) -> dict:  # type: ignore[type-arg]
        if not prompt:
            prompt = settings.DEFAULT_TEST_PROMPT

        logger.info(f"Test run with prompt: {prompt}")
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

    def embed_query(self, text: str) -> list[float]:
        return self.embeddings_model.embed_query(text)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.embeddings_model.embed_documents(texts)


def get_model_provider(model: ModelPublic) -> ModelProvider:
    provider_name = model.provider_name
    for cls in ModelProvider.implements:
        if cls.get_provider_name() == provider_name:
            return cls(model)

    raise BizException.create(ErrorCode.model_provider_not_supported,
                           provider_name)


_chat_model_cache: TTLCache[str, BaseChatModel] = TTLCache(
    maxsize=1000, ttl=10 * 60)  # 10min

_embeddings_cache: TTLCache[str, Embeddings] = TTLCache(
    maxsize=1000, ttl=10 * 60)  # 10min
