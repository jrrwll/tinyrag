from datetime import datetime

from pydantic import BaseModel

from app.config import settings
from app.core.rag.base import EmbeddingModelConfig, ProcessRule, \
    RetrievalModelConfig
from app.entities.knowledge import Knowledge
from app.util.json import load_and_update_dict


class KnowledgeCreate(BaseModel):
    name: str
    description: str | None = None

    process_rule: ProcessRule | None = None

    def to_entity(self) -> Knowledge:
        process_rule = self.process_rule
        if not process_rule:
            process_rule = settings.knowledge_default_process_rule
        return Knowledge(name=self.name, description=self.description,
                       process_rule=process_rule.model_dump_json())


class KnowledgeUpdate(KnowledgeCreate):
    id: str

    def update_entity(self, entity: Knowledge) -> None:
        update_dict = self.model_dump(exclude_none=True)
        update_dict.update(
            {
                "process_rule": self.process_rule.model_dump_json(),
            }
        )
        entity.sqlmodel_update(update_dict)


class KnowledgeImportFile(BaseModel):
    file_ids: list[str]


class KnowledgeImportStorage(BaseModel):
    file_path: str


class KnowledgeImportWebsite(BaseModel):
    pass


class KnowledgeImport(BaseModel):
    id: str

    file: KnowledgeImportFile | None = None
    storage: KnowledgeImportStorage | None = None
    website: KnowledgeImportWebsite | None = None


class SimpleKnowledgePublic(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime

    name: str
    description: str | None = None


class KnowledgePublic(SimpleKnowledgePublic):
    process_rule: ProcessRule | None = None
    embedding_model: EmbeddingModelConfig | None = None
    retrieval_model: RetrievalModelConfig | None = None

    @staticmethod
    def create(entity: Knowledge) -> "KnowledgePublic":
        entity_dict = entity.model_dump(exclude_none=True)
        load_and_update_dict(
            entity_dict,
            "process_rule", "embedding_model", "retrieval_model")
        return KnowledgePublic(**entity_dict)


class DocumentPreviewChunk(BaseModel):
    file_id: str
    process_rule: ProcessRule


class DocumentPreviewChunkPublic(BaseModel):
    content: list[str]


class KnowledgeChat(BaseModel):
    conversation_id: str
    query: str


class KnowledgeChatPublic(BaseModel):
    answer: str


class KnowledgeStreamChatPublic(BaseModel):
    answer: str
    done: bool | None = None
