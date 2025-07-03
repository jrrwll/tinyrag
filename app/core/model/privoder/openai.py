from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.core.model.privoder.base import ModelProvider
from app.entities.model import Model


class OpenaiModelSettings(BaseModel):
    group_id: str | None = None


class OpenAIModelProvider(ModelProvider):
    @staticmethod
    def get_provider_name() -> str:
        return "openai"

    def _create_chat_model(self, model: Model) -> BaseChatModel:
        return ChatOpenAI(
            base_url=model.base_url,
            api_key=model.api_key,  # type: ignore[arg-type]
            model=model.model_name,
        )
