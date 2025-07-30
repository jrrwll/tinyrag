from sqlmodel import Field

from app.core.rag.enums import DocumentSourceType
from app.entities.base import BizTableBase, enum_field_info


class Knowledge(BizTableBase, table=True):
    tenant_id: int
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    enable: bool = True

    process_rule: str | None = None
    embedding_model: str | None = None
    retrieval_model: str | None = None

    @staticmethod
    def get_collection_name(knowledge_id: str) -> str:
        return f"Knowledge_{knowledge_id}"


class KnowledgeDocument(BizTableBase, table=True):
    tenant_id: int
    knowledge_id: int
    position: int
    word_count: int = 0

    source_type: DocumentSourceType = enum_field_info(DocumentSourceType)
    source_info: str | None = None
    indexing: bool = False


class KnowledgeDocumentChunk(BizTableBase, table=True):

    tenant_id: int
    knowledge_id: int
    document_id: int
    position: int
    content: str = Field(max_length=10000)
    word_count: int = 0
    keywords: str | None = None
    index_doc_id: str | None = None


class KnowledgeConversation(BizTableBase, table=True):

    tenant_id: int
    knowledge_id: int


class KnowledgeMessage(BizTableBase, table=True):
    tenant_id: int
    knowledge_id: int
    conversation_id: int
    query: str
    answer: str | None = None
    error: str | None = None
