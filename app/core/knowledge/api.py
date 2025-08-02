from datetime import datetime
from pydoc import describe
from typing import Self

from pydantic import BaseModel

from app.config import settings
from app.core.knowledge.base import EmbeddingModelConfig, ProcessRule, \
    RetrievalModelConfig
from app.core.model.base import LlmModelConfig
from app.core.vector_store.base import VectorStoreConfig
from app.entities.knowledge import Knowledge
from app.util.model import dump_and_update_dict, load_and_update_dict


class KnowledgeCreate(BaseModel):
    workspace_id: int
    name: str
    description: str | None = None

    process_rule: ProcessRule | None = None
    llm_model_config: LlmModelConfig | None = None
    embedding_model_config: EmbeddingModelConfig | None = None
    vector_store_config: VectorStoreConfig | None = None
    retrieval_model_config: RetrievalModelConfig | None = None

    def to_entity(self) -> Knowledge:
        entity_dict = self.model_dump(exclude_none=True)
        if not entity_dict.get("process_rule"):
            entity_dict["process_rule"] = settings.default_process_rule

        dump_and_update_dict(
            entity_dict, "process_rule", "llm_model_config",
            "embedding_model_config", "vector_store_config",
            "retrieval_model_config"
        )
        return Knowledge(**entity_dict)


class KnowledgeUpdate(BaseModel):
    id: int
    name: str
    description: str | None = None

    def update_entity(self, entity: Knowledge) -> None:
        update_dict = self.model_dump()
        entity.sqlmodel_update(update_dict)


class KnowledgeUpdateConfig(BaseModel):
    id: int

    process_rule: ProcessRule | None = None
    llm_model_config: LlmModelConfig | None = None
    embedding_model_config: EmbeddingModelConfig | None = None
    vector_store_config: VectorStoreConfig | None = None
    retrieval_model_config: RetrievalModelConfig | None = None

    def update_entity(self, entity: Knowledge) -> None:
        update_dict = self.model_dump(exclude_none=True)
        dump_and_update_dict(update_dict, *self.model_fields_set)
        entity.sqlmodel_update(update_dict)


class KnowledgeImportFile(BaseModel):
    file_ids: list[str]


class KnowledgeImportStorage(BaseModel):
    file_path: str


class KnowledgeImportWebsite(BaseModel):
    page_urls: list[str]


class KnowledgeImport(BaseModel):
    id: int

    file: KnowledgeImportFile | None = None
    storage: KnowledgeImportStorage | None = None
    website: KnowledgeImportWebsite | None = None


class SimpleKnowledgePublic(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    name: str
    description: str | None = None


class KnowledgePublic(SimpleKnowledgePublic):
    process_rule: ProcessRule
    llm_model_config: LlmModelConfig
    embedding_model_config: EmbeddingModelConfig
    vector_store_config: VectorStoreConfig
    retrieval_model_config: RetrievalModelConfig | None = None

    @staticmethod
    def create(entity: Knowledge) -> "KnowledgePublic":
        entity_dict = entity.model_dump(exclude_none=True)
        load_and_update_dict(
            entity_dict, process_rule=ProcessRule,
            llm_model_config=LlmModelConfig,
            embedding_model_config=EmbeddingModelConfig,
            vector_store_config=VectorStoreConfig,
            retrieval_model_config=RetrievalModelConfig
        )
        return KnowledgePublic(**entity_dict)


class DocumentPreviewChunk(BaseModel):
    file_id: str
    process_rule: ProcessRule


class DocumentPreviewChunkPublic(BaseModel):
    content: list[str]


class KnowledgeStartConversation(BaseModel):
    knowledge_id: int


class KnowledgeChat(BaseModel):
    conversation_id: str
    query: str


class KnowledgeChatPublic(BaseModel):
    answer: str


class KnowledgeStreamChatPublic(BaseModel):
    answer: str
    done: bool | None = None
