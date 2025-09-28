from datetime import datetime
from typing import Self

from pydantic import BaseModel, Field, model_validator

from app.core.knowledge.base import EmbeddingModelConfig, ProcessRule, \
    RetrievalModelConfig
from app.core.knowledge.enums import DocumentSourceType
from app.core.model.base import LlmModelConfig
from app.core.vector_store.base import VectorStoreConfig
from app.entities.knowledge import Knowledge, KnowledgeDocument
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

    @model_validator(mode="after")
    def _validate(self) -> Self:
        if (not self.process_rule and not self.llm_model_config
                and not self.embedding_model_config
                and not self.vector_store_config and not self.retrieval_model_config):
            raise ValueError("at least one config is required")
        return self

    def update_entity(self, entity: Knowledge) -> None:
        update_dict = self.model_dump(exclude_none=True)
        dump_and_update_dict(update_dict, *self.model_fields_set)
        entity.sqlmodel_update(update_dict)


class KnowledgeImportFile(BaseModel):
    file_ids: list[str] = Field(min_length=1, max_length=1000)


class KnowledgeImportStorage(BaseModel):
    storage_id: int | None = None
    file_path: str


class KnowledgeImportWebsite(BaseModel):
    page_urls: list[str]


class KnowledgeImport(BaseModel):
    id: int

    process_rule: ProcessRule | None = None
    file: KnowledgeImportFile | None = None
    storage: KnowledgeImportStorage | None = None
    website: KnowledgeImportWebsite | None = None

    @model_validator(mode="after")
    def _validate(self) -> Self:
        if not self.file and not self.storage and not self.website:
            raise ValueError("file or storage or website is required")
        return self


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

    @classmethod
    def create(cls, entity: Knowledge) -> Self:
        entity_dict = entity.model_dump(exclude_none=True)
        load_and_update_dict(
            entity_dict, process_rule=ProcessRule,
            llm_model_config=LlmModelConfig,
            embedding_model_config=EmbeddingModelConfig,
            vector_store_config=VectorStoreConfig,
            retrieval_model_config=RetrievalModelConfig
        )
        return cls(**entity_dict)


class DocumentPreviewChunk(BaseModel):
    process_rule: ProcessRule | None = None

    file_id: str | None = None

    storage_id: int | None = None
    storage_file_path: str | None = None

    @model_validator(mode="after")
    def _validate(self) -> Self:
        if not self.file_id and self.storage_file_path is None:
            raise ValueError("file_id or storage_file_path is required")
        return self


class DocumentPreviewChunkPublic(BaseModel):
    content: list[str]


class KnowledgeDocumentPublic(BaseModel):
    process_rule: str
    position: int
    word_count: int = 0

    source_type: DocumentSourceType
    source_info: str | None = None
    indexing: bool = False

    @classmethod
    def create(cls, entity: KnowledgeDocument) -> Self:
        entity_dict = entity.model_dump(exclude_none=True)
        return cls(**entity_dict)


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
