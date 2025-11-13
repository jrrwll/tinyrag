import threading
from abc import ABC, abstractmethod
from typing import MutableMapping

from pydantic import BaseModel

from app.common.error_code import BizException, ErrorCode
from app.core.meta.provider import MetaProvider
from app.core.model.api import ModelPublic
from app.core.model.enums import ModelType
from corepy.codec import md5
from corepy.lang import find_sub_types


class ModelProvider[Cfg: BaseModel, M](MetaProvider[Cfg], ABC):

    def __init__(self, model: ModelPublic):
        super().__init__(model.config)

        self.model_name: str = model.model_name
        self._footprint: str = md5(model.model_dump_json())

    @staticmethod
    @abstractmethod
    def get_model_type() -> ModelType:
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def get_provider_name() -> str:
        raise NotImplementedError()

    @abstractmethod
    def _create_model(self) -> M:
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def _model_cache() -> MutableMapping[str, M]:
        raise NotImplementedError()

    @property
    def model(self) -> M:
        cache = self._model_cache()
        item = cache.get(self._footprint)
        if item:
            return item
        item = self._create_model()
        cache[self._footprint] = item
        return item


class ModelProviderFactory:
    _lock = threading.Lock()
    _initialized = False
    # model_type -> provider_name -> cls
    _implements: dict[ModelType, dict[str, type]] = {}

    @classmethod
    def get_implements(cls, model_type: ModelType) -> dict[
        str, type[ModelProvider]]:
        cls._ensure_provider_classes()

        return cls._implements.get(model_type, {})

    @classmethod
    def get_provider_class(cls, model_type: ModelType,
            provider_name: str) -> type:
        cls._ensure_provider_classes()

        classes = cls._implements.get(model_type, {})
        c = classes.get(provider_name)
        if not c:
            raise BizException.create(
                ErrorCode.model_provider_not_supported,
                model_type=model_type, provider_name=provider_name)
        return c

    @classmethod
    def _ensure_provider_classes(cls) -> None:
        if cls._initialized:
            return

        with cls._lock:
            if cls._initialized:
                return

            cls._implements.clear()

            from app.core import model as model_mod

            provider_classes = find_sub_types(
                ModelProvider, model_mod, exclude_abc=True)
            for c in provider_classes:
                classes = cls._implements.get(c.get_model_type())
                if not classes:
                    classes = {}
                    cls._implements[c.get_model_type()] = classes

                classes[c.get_provider_name()] = c

            cls._initialized = True
