from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.core.model.privoder.base import ModelProvider


class OpenaiModelSettings(BaseModel):
    group_id: str | None = None


class OpenAIModelProvider(ModelProvider):
    @staticmethod
    def get_provider_name() -> str:
        return "openai"

    def _create_chat_model(self) -> BaseChatModel:
        base_url = self.model.base_url
        model_name = self.model.model_name
        api_key = self.model.api_key

        return ChatOpenAI(
            base_url=base_url,
            model=model_name,
            api_key=api_key,  # type: ignore[arg-type]
        )
