from datetime import datetime

from pydantic import BaseModel

from app.core.dataset.base import EmbeddingModelConfig, RetrievalModelConfig
from app.entities.dataset import Dataset


class DatasetImportCreate(BaseModel):
    file_ids: list[str]

    def to_entity(self) -> Dataset:
        pass


class DatasetImportUpdate(DatasetImportCreate):
    id: int


class SimpleDatasetPublic(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    name: str
    description: str | None = None


class DatasetPublic(SimpleDatasetPublic):
    embedding_model: EmbeddingModelConfig | None = None
    retrieval_model: RetrievalModelConfig | None = None

    def to_entity(self) -> Dataset:
        pass

    @staticmethod
    def new(entity: Dataset) -> "DatasetPublic":
        pass


class PreviewChunk(BaseModel):
    file_id: str
    chunk_overlap: int | None = None
    chunk_size: int | None = None
    separators: list[str] | None = None


class PreviewChunkPublic(BaseModel):
    content: list[str]

