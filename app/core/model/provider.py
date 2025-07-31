import threading
from abc import ABC, abstractmethod
from typing import MutableMapping, Type

from pydantic import BaseModel

from app.common.error_code import BizException, ErrorCode
from app.core.model.api import ModelPublic
from app.core.model.enums import ModelType
from app.util.codec import md5
from app.util.lang import find_sub_types


class BaseModelProvider[T: BaseModel, M](ABC):

    def __init__(self, model: ModelPublic):
        self.model_name: str = model.model_name
        self.model_config: T = self.get_config_type().model_validate(
            model.config)
        self._model_footprint: str = md5(model.model_dump_json())

    @staticmethod
    @abstractmethod
    def get_model_type() -> ModelType:
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def get_provider_name() -> str:
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def get_config_type() -> Type[T]:
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
        item = cache.get(self._model_footprint)
        if item:
            return item
        item = self._create_model()
        cache[self._model_footprint] = item
        return item


class ModelProviderFactory:

    _lock = threading.Lock()
    _initialized = False
    _implements: dict[ModelType, dict[str, type]] = {}

    @classmethod
    def get_provider_class(cls, model_type: ModelType,
            provider_name: str) -> type:
        if not cls._initialized:
            cls.load_provider_classes()

        classes = cls._implements.get(model_type, {})
        c =  classes.get(provider_name)
        if not c:
            raise BizException.create(
                ErrorCode.model_provider_not_supported,
                model_type, provider_name)
        return c

    @classmethod
    def load_provider_classes(cls) -> None:
        with cls._lock:
            cls._implements.clear()

            from app.core import model as model_mod

            provider_classes = find_sub_types(BaseModelProvider, model_mod)
            for c in provider_classes:
                classes = cls._implements.get(c.get_model_type())
                if not classes:
                    classes = {}
                    cls._implements[c.get_model_type()] = classes

                classes[c.get_provider_name()] = c

            if not cls._initialized:
                cls._initialized = True
