from typing import Self

from pydantic import BaseModel, model_validator

from app.common.error_code import BizException, ErrorCode
from app.core.model.builtin_models import is_valid_model_name
from app.core.model.enums import ModelType


class TextSplitterRule(BaseModel):
    chunk_overlap: int | None = None
    chunk_size: int | None = None
    separators: list[str] | None = None


class ProcessRule(BaseModel):
    text_splitter: TextSplitterRule


class EmbeddingModelConfig(BaseModel):
    model_id: int | None = None
    model_name: str | None = None # sentence-transformers

    top_k: int = 4

    @model_validator(mode="after")
    def _validate(self) -> Self:
        if not self.model_id and not self.model_name:
            raise ValueError("Embedding model id or name is required")

        if self.model_id:
            return

        if not is_valid_model_name(ModelType.TextEmbedding, self.model_name):
            raise BizException.create(ErrorCode.model_name_not_supported, self.model_name)


class RetrievalModelConfig(BaseModel):
    top_k: int
    reranking_model_id: int
