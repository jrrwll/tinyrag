from typing import Self

from pydantic import BaseModel, model_validator

from app.core.model.api import ModelPublic
from app.core.model.enums import EmbeddingType


class LlmModelConfig(BaseModel):
    model_id:  int
    temperature: float = 0.7


class EmbeddingModelConfig(BaseModel):
    embedding_type: EmbeddingType
    model_id: int | None
    model_name: str | None

    top_k: int = 4

    @model_validator(mode="after")
    def _validate(self) -> Self:
        if self.embedding_type == EmbeddingType.Provider:
            if self.model_id is None:
                raise ValueError("model_id is required when embedding_type is provider")
        elif self.embedding_type == EmbeddingType.Transformer:
            if self.model_name is None:
                raise ValueError("model_name is required when embedding_type is transformer")
            elif not EmbeddingType.is_valid_model_name(self.model_name):
                raise ValueError("model_name is invalid")

class VectorStoreConfig(BaseModel):
    vector_id: int


class WorkspaceDetail(BaseModel):
    id: int
    name: str

    llm_model: ModelPublic | None = None
    embedding_model: ModelPublic | None = None
