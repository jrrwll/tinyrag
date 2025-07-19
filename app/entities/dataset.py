from sqlmodel import Field

from app.entities.base import TableBase


class Dataset(TableBase, table=True):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    enable: bool = Field(default=True)

    process_rule: str | None = None
    embedding_model: str | None = None
    retrieval_model: str | None = None


class Document(TableBase, table=True):
    dataset_id: int
    position: int
    file_id: str | None = None
    word_count: int = 0


class DocumentChunk(TableBase, table=True):

    __tablename__ = 'document_chunk'

    dataset_id: int
    document_id: int
    position: int
    content: str = Field(max_length=10000)
    word_count: int = 0
    keywords: str

