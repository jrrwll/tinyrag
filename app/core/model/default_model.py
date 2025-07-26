from cachetools import TTLCache

from app.common.error_code import BizException, ErrorCode
from app.core.model.enums import ModelType
from app.entities.dao.model import get_default_models
from app.entities.model import Model
from app.util.data import OptionalValue

# TODO broadcast to clear caches
_default_model_cache: TTLCache[
    ModelType, OptionalValue[Model]] = TTLCache(
    maxsize=10, ttl=10 * 60)  # 10min


def get_default_model(model_type: ModelType) -> Model:
    model = _default_model_cache.get(model_type)
    if model:
        return model.value

    models = get_default_models()

    for member in ModelType:
        m = models.get(member)
        _default_model_cache[member] = OptionalValue(value=m)
        if m and member == model_type:
            model = m

    if not model:
        raise BizException.create(ErrorCode.default_model_not_set, model_type)
    return model
