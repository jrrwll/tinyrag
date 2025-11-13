from typing import Self
from uuid import uuid4

from langchain_core.documents import Document
from pydantic import BaseModel, model_validator

from app.core.knowledge.enums import DocumentFormatType
from corepy.model import new_validation_error


class DocumentModel(BaseModel):
    id: str
    content: str
    metadata: dict

    @staticmethod
    def create(document: Document) -> "DocumentModel":
        return DocumentModel(
            id=document.id or str(uuid4()),
            content=document.page_content,
            metadata=document.metadata
        )

    def to_document(self) -> Document:
        return Document(
            id=self.id,
            page_content=self.content,
            metadata=self.metadata
        )


class TextSplitterRule(BaseModel):
    type: DocumentFormatType = DocumentFormatType.Text
    chunk_overlap: int | None = None
    chunk_size: int | None = None
    separators: list[str] | None = None

    @model_validator(mode="after")
    def _validate(self) -> Self:
        if self.type == DocumentFormatType.Text:
            missing_fields = []
            if self.chunk_size is None:
                missing_fields.append("chunk_size")
            if self.chunk_overlap is None:
                missing_fields.append("chunk_overlap")
            if not self.separators:
                missing_fields.append("separators")
            if missing_fields:
                raise new_validation_error(self, missing_fields)
        return self
