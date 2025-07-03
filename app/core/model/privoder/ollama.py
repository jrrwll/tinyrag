from langchain_core.language_models import BaseChatModel
from langchain_ollama import ChatOllama
from pydantic import BaseModel

from app.core.model.privoder.base import ModelProvider
from app.entities.model import Model


# settings = OllamaModelSettings.model_validate_json(model.settings)
class OllamaModelSettings(BaseModel):
    content_length: int = 4096
    max_tokens: int = 4096
    function_calling: bool = False


class OllamaModelProvider(ModelProvider):
    @staticmethod
    def get_provider_name() -> str:
        return "ollama"

    def _create_chat_model(self, model: Model) -> BaseChatModel:
        return ChatOllama(base_url=model.base_url, model=model.model_name)
