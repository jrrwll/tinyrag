from typing import Iterable
from uuid import uuid4

from cachetools import TTLCache
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import TextLoader
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter, \
    TextSplitter
from pydantic import BaseModel

from app.core.file.enums import FileType
from app.core.knowledge.base import ProcessRule
from app.util.codec import md5


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


class TextProcessor():
    text_splitter: TextSplitter

    def __init__(self, process_rule: ProcessRule):
        text_splitter = process_rule.text_splitter

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=text_splitter.chunk_size,
            chunk_overlap=text_splitter.chunk_overlap,
            separators=text_splitter.separators,
            add_start_index=True
        )

    def split_documents(self,
            documents: Iterable[DocumentModel]) -> Iterable[DocumentModel]:
        for document in documents:
            docs = self.text_splitter.split_documents([document.to_document()])
            for doc in docs:
                yield DocumentModel.create(doc)

    def load_documents(self, file_path: str, file_type: FileType,
            password: str | bytes | None = None,
            encoding: str | None = None) -> Iterable[DocumentModel]:
        loader = self._new_loader(file_path, file_type, password, encoding)
        for doc in loader.lazy_load():
            yield DocumentModel.create(doc)

    @staticmethod
    def _new_loader(file_path: str, file_type: FileType,
            password: str | bytes | None = None,
            encoding: str | None = None) -> BaseLoader:
        if file_type == FileType.Pdf:
            return PyPDFLoader(file_path, password=password)
        elif file_type == FileType.Doc:
            return Docx2txtLoader(file_path)
        else:
            if encoding:
                return TextLoader(file_path, encoding=encoding)
            else:
                return TextLoader(file_path, autodetect_encoding=True)


_cache: TTLCache[str, TextProcessor] = TTLCache(
    maxsize=1024, ttl=3600)


def get_text_processor(process_rule: ProcessRule) -> TextProcessor:
    footprint = md5(process_rule.model_dump_json())
    text_processor = _cache.get(footprint)
    if not text_processor:
        text_processor = TextProcessor(process_rule)
        _cache[footprint] = text_processor

    return text_processor
