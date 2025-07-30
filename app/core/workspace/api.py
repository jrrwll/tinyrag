from datetime import datetime

from pydantic import BaseModel

from app.core.workspace.base import EmbeddingModelConfig, LlmModelConfig, \
    VectorStoreConfig
from app.entities.workspace import Workspace
from app.util.json import load_and_update_dict


class SimpleWorkspacePublic(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    name: str
    description: str | None = None


class WorkspacePublic(SimpleWorkspacePublic):
    llm_model_config:  LlmModelConfig | None = None
    embedding_model_config:  EmbeddingModelConfig | None = None
    vector_store_config:  VectorStoreConfig | None = None

    @staticmethod
    def create(entity: Workspace) -> "WorkspacePublic":
        entity_dict = entity.model_dump(exclude_none=True)
        load_and_update_dict(entity_dict, "llm_model_config", "embedding_model_config")
        return WorkspacePublic(**entity_dict)


class WorkspaceCreate(BaseModel):
    name: str
    description: str | None = None

    def to_entity(self) -> Workspace:
        entity_dict = self.model_dump(exclude_none=True)
        return Workspace(**entity_dict)


class WorkspaceUpdate(WorkspaceCreate):
    id: int

    def update_entity(self, entity: Workspace) -> None:
        update_dict = self.model_dump(exclude_none=True)
        entity.sqlmodel_update(update_dict)


class WorkspaceUpdateConfig(BaseModel):
    id: int

    llm_model_config:  LlmModelConfig | None = None
    embedding_model_config:  EmbeddingModelConfig | None = None
    vector_store_config:  VectorStoreConfig | None = None


class WorkspaceUnsetConfig(BaseModel):
    id: int

    llm_model_config: bool = False
    embedding_model_config: bool = False
    vector_store_config: bool = False
