from app.common.deps import SessionDep
from app.common.error_code import BizException, ErrorCode
from app.core.model.api import ModelTestRun, ModelTestRunPublic
from app.entities.model import Model
from app.services.model.base import ModelProvider
from app.services.model.ollama import OllamaModelProvider
from app.services.model.opanai import OpenAIModelProvider


def test_run_model(
    _: SessionDep, params: ModelTestRun, model: Model
) -> ModelTestRunPublic:
    provider_name = model.provider_name

    provider = get_model_provider(provider_name)
    return provider.test_run(params, model)


_model_providers: dict[str, ModelProvider] = {
    OllamaModelProvider.get_provider_name(): OllamaModelProvider(),
    OpenAIModelProvider.get_provider_name(): OpenAIModelProvider(),
}


def get_model_provider(provider_name: str) -> ModelProvider:
    provider = _model_providers.get(provider_name)
    if provider:
        return provider
    else:
        raise BizException.new(ErrorCode.model_provider_not_supported, provider_name)
