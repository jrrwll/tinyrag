import json
from typing import Callable, Iterable, Self
from uuid import uuid4

from cachetools import TTLCache
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader, \
    TextLoader
from langchain_core.document_loaders import BaseLoader
from langchain_text_splitters import CharacterTextSplitter, MarkdownTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter, \
    TextSplitter

from app.core.file.enums import FileType
from app.core.knowledge.base import ProcessRule
from app.core.knowledge.enums import DocumentFormatType
from app.core.knowledge.text.base import DocumentModel
from app.core.knowledge.text.tokens import split_text
from corepy.codec import md5


class TextProcessor():
    text_splitter: TextSplitter | None

    @classmethod
    def get_processor(cls, process_rule: ProcessRule) -> Self:
        footprint = md5(process_rule.model_dump_json(exclude_none=True))
        text_processor = _cache.get(footprint)
        if not text_processor:
            text_processor = cls(process_rule)
            _cache[footprint] = text_processor

        return text_processor

    def __init__(self, process_rule: ProcessRule):
        self.split_func: Callable[[Iterable[DocumentModel]],
        Iterable[DocumentModel]] | None = None
        self.text_splitter: TextSplitter | None = None

        text_splitter = process_rule.text_splitter
        document_format = text_splitter.type
        if document_format == DocumentFormatType.JsonList:
            self.split_func = _json_list_split_documents
        elif document_format == DocumentFormatType.TextLine:
            self.text_splitter = CharacterTextSplitter("\n")
        elif document_format == DocumentFormatType.Markdown:
            self.text_splitter = MarkdownTextSplitter()
        else:
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=text_splitter.chunk_size,
                chunk_overlap=text_splitter.chunk_overlap,
                separators=text_splitter.separators,
                add_start_index=True
            )

    @staticmethod
    def load_documents(file_path: str, file_type: FileType,
            password: str | bytes | None = None,
            encoding: str | None = None) -> Iterable[DocumentModel]:
        loader = _new_loader(file_path, file_type, password, encoding)
        for doc in loader.lazy_load():
            yield DocumentModel.create(doc)

    def split_documents(self,
            documents: Iterable[DocumentModel]
    ) -> Iterable[DocumentModel]:
        if self.split_func:
            yield from self.split_func(documents)
        else:
            for document in documents:
                docs = self.text_splitter.split_documents(
                    [document.to_document()])
                for doc in docs:
                    yield DocumentModel.create(doc)


_cache: TTLCache[str, TextProcessor] = TTLCache(
    maxsize=1024, ttl=3600)


def _json_list_split_documents(
        documents: Iterable[DocumentModel]
) -> Iterable[DocumentModel]:
    for doc in documents:
        metadata, content = doc.metadata, doc.content
        elems = None
        try:
            elems = json.loads(content)
        except json.JSONDecodeError:
            pass
        if elems is None or not isinstance(elems, list):
            elems = split_text(content)

        for elem in elems:
            yield DocumentModel(
                id=str(uuid4()),
                content=json.dumps(elem, ensure_ascii=False),
                metadata=metadata
            )


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
