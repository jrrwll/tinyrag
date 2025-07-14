from datetime import datetime

from pydantic import BaseModel

from app.entities.dataset import Dataset


class DatasetImportCreate(BaseModel):
    file_ids: list[str]

    def to_entity(self) -> Dataset:
        pass


class DatasetImportUpdate(DatasetImportCreate):
    id: int


class DatasetPublic(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    name: str
    description: str | None = None


class SimpleDatasetPublic(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    name: str
    description: str | None = None


class PreviewChunk(BaseModel):
    file_id: str
    chunk_overlap: int
    chunk_size: int
    separator: str


class PreviewChunkPublic(BaseModel):
    total_segments: int
    content: list[str]

