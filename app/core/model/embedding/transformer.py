from typing import Type

from sentence_transformers import SentenceTransformer
from langchain_core.embeddings import Embeddings

from app.config import settings
from app.core.model.embedding.base import EmbeddingProvider
from app.core.model.enums import BUILTIN_MODEL_PROVIDER_NAME
from app.util.model import EmptyBaseModel


class TransformerEmbedding(Embeddings):

    def __init__(self, model_name: str):
        model_path = f"{settings.MODEL_DIRECTORY}/{model_name}"
        self.transformer = SentenceTransformer(model_path)

    def embed_query(self, text: str) -> list[float]:
        return self.transformer.encode(text, normalize_embeddings=True).tolist()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        vecs = self.transformer.encode(texts, normalize_embeddings=True)
        return vecs.tolist()


class TransformerEmbeddingProvider(EmbeddingProvider[EmptyBaseModel]):

    @staticmethod
    def get_provider_name() -> str:
        raise BUILTIN_MODEL_PROVIDER_NAME

    @staticmethod
    def get_config_type() -> Type[EmptyBaseModel]:
        return EmptyBaseModel

    def _create_model(self) -> Embeddings:
        return TransformerEmbedding(self.model_name)
