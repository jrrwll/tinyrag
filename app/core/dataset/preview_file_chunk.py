from app.common.error_code import BizException, ErrorCode
from app.core.dataset.api import PreviewChunk, PreviewChunkPublic

from app.core.model.default_model import get_default_model_provider
from app.core.model.enums import ModelType


def preview_file_chunk(params: PreviewChunk) -> PreviewChunkPublic:
    embedding = get_default_model_provider(ModelType.TextEmbedding)
    if not embedding:
        raise BizException.new(ErrorCode.default_model_not_set, ModelType.TextEmbedding)
    embeddings_model = embedding.embeddings_model

    embeddings_model.embed_documents()
