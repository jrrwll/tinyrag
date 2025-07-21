import json
from datetime import datetime

from pydantic import BaseModel

from app.config import settings
from app.core.dataset.base import EmbeddingModelConfig, ProcessRule, \
    RetrievalModelConfig
from app.entities.dataset import Dataset
from app.util.json import load_and_update_dict


class DatasetCreate(BaseModel):
    name: str
    description: str | None = None

    process_rule: ProcessRule | None = None

    def to_entity(self) -> Dataset:
        process_rule = self.process_rule
        if not process_rule:
            process_rule = settings.dataset_default_process_rule
        return Dataset(name=self.name, description=self.description,
                process_rule=process_rule.model_dump_json())


class DatasetUpdate(DatasetCreate):
    id: int

    def update_entity(self, entity: Dataset) -> None:
        update_dict = self.model_dump(exclude_none=True)
        update_dict.update(
            {
                "process_rule": self.process_rule.model_dump_json(),
            }
        )
        entity.sqlmodel_update(update_dict)


class DatasetImportFile(BaseModel):
    file_ids: list[str]


class DatasetImportRemoteFile(BaseModel):
    file_dir: str


class DatasetImportWebsite(BaseModel):
    file_ids: list[str]


class DatasetImport(BaseModel):
    id: int

    file: DatasetImportFile | None = None
    remote_file: DatasetImportRemoteFile | None = None
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
