from langchain_core.embeddings import Embeddings
from langchain_core.language_models import BaseChatModel
from langchain_ollama import ChatOllama, OllamaEmbeddings
from pydantic import BaseModel

from app.core.model.privoder.base import ModelProvider


# settings = OllamaModelSettings.model_validate_json(model.settings)
class OllamaModelSettings(BaseModel):
    content_length: int = 4096
    max_tokens: int = 4096
    function_calling: bool = False


class OllamaModelProvider(ModelProvider):

    @staticmethod
    def get_provider_name() -> str:
        return "ollama"

    def _create_chat_model(self) -> BaseChatModel:
        base_url = self.model.base_url
        model_name = self.model.model_name
        return ChatOllama(base_url=base_url, model=model_name)

    def _create_text_embedding(self) -> Embeddings:
        base_url = self.model.base_url
        model_name = self.model.model_name
        return OllamaEmbeddings(base_url=base_url, model=model_name)
