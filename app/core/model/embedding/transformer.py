import logging
import multiprocessing
import os.path
from typing import Type

from langchain_core.embeddings import Embeddings
from pydantic import ConfigDict

from app.config import settings
from app.core.model.builtin_models import BuiltinModel
from app.core.model.embedding.base import BaseEmbeddingConfig, EmbeddingProvider
from app.core.model.enums import BUILTIN_MODEL_PROVIDER_NAME

logger = logging.getLogger(__name__)

"""
huggingface-cli download \
  nomic-ai/nomic-embed-text-v1.5 \
  --local-dir ./nomic-embed-text-v1.5 \
  --local-dir-use-symlinks False
"""


class TransformerEmbeddingConfig(BaseEmbeddingConfig):
    model_config = ConfigDict(json_schema_extra={"builtin": True})

    repo_name: str | None = None


class TransformerEmbedding(Embeddings):
    _lock = multiprocessing.Lock()

    def __init__(self, model_name: str, model_config: BuiltinModel):
        from sentence_transformers import SentenceTransformer

        model_path = self._ensure_model_path(model_name, model_config)
        self.transformer = SentenceTransformer(
            model_path, trust_remote_code=True)

    def embed_query(self, text: str) -> list[float]:
        return self.transformer.encode(text, normalize_embeddings=True).tolist()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        vecs = self.transformer.encode(texts, normalize_embeddings=True)
        return vecs.tolist()

    @staticmethod
    def _ensure_model_path(model_name: str, model_config: BuiltinModel) -> str:
        repo_name = 'sentence-transformers'
        if model_config.repo_name:
            repo_name = model_config.repo_name

        model_path = f"{settings.MODEL_DIRECTORY}/{model_name}"
        if not os.path.exists(model_path):
            with TransformerEmbedding._lock:
                if not os.path.exists(model_path):
                    from huggingface_hub import snapshot_download

                    repo_id = f"{repo_name}/{model_name}"
                    logger.info(
                        f"snapshot_download model {repo_id} to {model_path}")
                    snapshot_download(
                        repo_id=repo_id,
                        local_dir=model_path,
                        local_dir_use_symlinks=False,
                    )
        return model_path


class TransformerEmbeddingProvider(
    EmbeddingProvider[TransformerEmbeddingConfig]):

    @staticmethod
    def get_provider_name() -> str:
        return BUILTIN_MODEL_PROVIDER_NAME

    @staticmethod
    def get_config_type() -> Type[TransformerEmbeddingConfig]:
        return TransformerEmbeddingConfig

    def _create_model(self) -> Embeddings:
        return TransformerEmbedding(self.model_name, self.config)
