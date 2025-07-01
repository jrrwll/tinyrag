from abc import ABC, abstractmethod

from cachetools import TTLCache
from langchain_core.language_models import BaseChatModel

from app.entities.model import Model
from app.schemas.model import ModelTestRun, ModelTestRunPublic


class ModelProvider(ABC):
    # ttl seconds
    _cache: TTLCache[int, BaseChatModel] = TTLCache(maxsize=100, ttl=30 * 60)

    @staticmethod
    @abstractmethod
    def get_provider_name() -> str:
        pass

    def _get_chat_model(self, model: Model) -> BaseChatModel:
        model_id = model.id
        if model_id in self._cache:
            return self._cache[model_id]

        chat_model = self._create_chat_model(model)
        self._cache[model_id] = chat_model
        return chat_model

    @abstractmethod
    def _create_chat_model(self, model: Model) -> BaseChatModel:
        pass

    def test_run(self, params: ModelTestRun, model: Model) -> ModelTestRunPublic:
        prompt = params.prompt
        if not prompt:
            prompt = "Hi!"

        chat_model = self._get_chat_model(model)

        # AiMessage
        msg = chat_model.invoke(prompt)
        return ModelTestRunPublic(test_result=msg.model_dump())
