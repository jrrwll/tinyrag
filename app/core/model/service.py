from app.common.error_code import BizException, ErrorCode
from app.core.model.privoder.base import ModelProvider
from app.core.model.privoder.ollama import OllamaModelProvider
from app.core.model.privoder.openai import OpenAIModelProvider

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
