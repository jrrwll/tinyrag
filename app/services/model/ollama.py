from langchain_core.language_models import BaseChatModel
from langchain_ollama import ChatOllama

from app.entities.model import Model
from app.services.model.base import ModelProvider


class OllamaModelProvider(ModelProvider):
    @staticmethod
    def get_provider_name() -> str:
        return "ollama"

    def _create_chat_model(self, model: Model) -> BaseChatModel:
        return ChatOllama(base_url=model.base_url, model=model.model_name)
