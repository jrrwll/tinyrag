from sqlmodel import Field

from app.core.knowledge.enums import DocumentSourceType
from app.entities.base import BizTableBase, LogTableBase, enum_field_info


class Knowledge(BizTableBase, table=True):
    tenant_id: int
    workspace_id: int
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    enable: bool = True

    process_rule: str
    llm_model_config: str
    embedding_model_config: str
    vector_store_config: str
    retrieval_model_config: str | None = None

    @staticmethod
    def get_collection_name(knowledge_id: int) -> str:
        return f"knowledge_{knowledge_id}"


class KnowledgeDocument(LogTableBase, table=True):
    id: str = Field(primary_key=True)

    tenant_id: int
    workspace_id: int
    knowledge_id: int

    position: int
    word_count: int = 0

    source_type: DocumentSourceType = enum_field_info(DocumentSourceType)
    source_info: str | None = None
    indexing: bool = False


class KnowledgeDocumentChunk(LogTableBase, table=True):
    id: str = Field(primary_key=True)

    tenant_id: int
    workspace_id: int
    knowledge_id: int
    document_id: str

    position: int
    content: str = Field(max_length=10000)
    word_count: int = 0
    keywords: str | None = None


class KnowledgeConversation(BizTableBase, table=True):
    tenant_id: int
    workspace_id: int
    knowledge_id: int


class KnowledgeMessage(BizTableBase, table=True):
    tenant_id: int
    workspace_id: int
    knowledge_id: int
    conversation_id: int

    query: str
    answer: str | None = None
    error: str | None = None
