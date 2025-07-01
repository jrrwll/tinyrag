from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

from app.entities.model import Model
from app.services.model.base import ModelProvider


class OpenAIModelProvider(ModelProvider):
    @staticmethod
    def get_provider_name() -> str:
        return "openai"

    def _create_chat_model(self, model: Model) -> BaseChatModel:
        return ChatOpenAI(
            base_url=model.base_url, api_key=model.api_key, model=model.model_name
        )
