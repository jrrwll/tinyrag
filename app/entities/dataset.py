from sqlmodel import Field

from app.core.rag.enums import DocumentSourceType
from app.entities.base import TableBase, enum_field_info


class Dataset(TableBase, table=True):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    enable: bool = True

    process_rule: str | None = None
    embedding_model: str | None = None
    retrieval_model: str | None = None

    @staticmethod
    def get_collection_name(dataset_id: str) -> str:
        return f"dataset_{dataset_id}"


class Document(TableBase, table=True):
    dataset_id: int
    position: int
    word_count: int = 0

    source_type: DocumentSourceType = enum_field_info(DocumentSourceType)
    source_info: str | None = None
    indexing: bool = False


class DocumentChunk(TableBase, table=True):

    __tablename__ = 'document_chunk'

    dataset_id: int
    document_id: int
    position: int
    content: str = Field(max_length=10000)
    word_count: int = 0
    keywords: str | None = None
    index_doc_id: str | None = None


class DatasetConversation(TableBase, table=True):

    __tablename__ = 'dataset_conversation'

    dataset_id: int


class DatasetMessage(TableBase, table=True):
    conversation_id: int
    query: str
    answer: str | None = None
    error: str | None = None
