from cachetools import TTLCache

from app.core.model.api import ModelPublic
from app.core.model.enums import ModelType
from app.core.model.privoder import ModelProvider
from app.core.model.privoder.base import get_model_provider
from app.entities.dao.model import get_default_models
from app.entities.model import Model
from app.util.data import OptionalValue

# TODO broadcast to clear caches
_default_model_cache: TTLCache[
    ModelType, OptionalValue[Model]] = TTLCache(
    maxsize=10, ttl=10 * 60)  # 10min


def get_default_model(model_type: ModelType) -> Model | None:
    model = _default_model_cache.get(model_type)
    if model:
        return model.value

    models = get_default_models()

    for member in ModelType:
        m = models.get(member)
        _default_model_cache[member] = OptionalValue(value=m)
        if m and member == model_type:
            model = m

    return model


def get_default_model_provider(model_type: ModelType) -> ModelProvider | None:
    model = get_default_model(model_type)
    if not model:
        return None

    return get_model_provider(ModelPublic.create(model))
