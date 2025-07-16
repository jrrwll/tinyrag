from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel

from app.core.dataset.base import EmbeddingModelConfig, ProcessRule, \
    RetrievalModelConfig
from app.entities.dataset import Dataset
from app.util.json import load_and_update_dict


class DatasetCreate(BaseModel):
    name: str
    description: str | None = None

    def to_entity(self) -> Dataset:
        pass


class DatasetUpdate(DatasetCreate):
    id: int


class DatasetImportFile(BaseModel):
    file_ids: list[str]


class DatasetImportWebsite(BaseModel):
    file_ids: list[str]


class DatasetImport(BaseModel):
    id: int

    file: DatasetImportFile | None = None
    website: DatasetImportWebsite | None = None


class SimpleDatasetPublic(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    name: str
    description: str | None = None


class DatasetPublic(SimpleDatasetPublic):
    process_rule: ProcessRule | None = None
    embedding_model: EmbeddingModelConfig | None = None
    retrieval_model: RetrievalModelConfig | None = None

    def to_entity(self) -> Dataset:
        pass

    @staticmethod
    def new(entity: Dataset) -> "DatasetPublic":
        entity_dict = entity.model_dump(exclude_none=True)
        load_and_update_dict(
            entity_dict, "process_rule", "embedding_model", "retrieval_model")
        return DatasetPublic(**entity_dict)


class PreviewChunk(BaseModel):
    file_id: str
    process_rule: ProcessRule


class PreviewChunkPublic(BaseModel):
    content: list[str]
