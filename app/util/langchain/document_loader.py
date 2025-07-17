from pathlib import Path
from typing import Iterator, Sequence

import bs4
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document


def load_web_page(web_paths: Sequence[str],
        tag: Sequence[str] | None = None,
        id: Sequence[str] | None = None,
        class_: Sequence[str] | None = None) -> Iterator[Document]:
    bs4_strainer = bs4.SoupStrainer(name=tag, id=id, class_=class_)
    loader = WebBaseLoader(
        web_paths=web_paths,
        bs_kwargs=dict(parse_only=bs4_strainer),
    )
    return loader.lazy_load()


def load_text(file_path: str | Path,
        encoding: str | None = None) -> Iterator[Document]:
    if encoding:
        loader = TextLoader(file_path, encoding=encoding)
    else:
        loader = TextLoader(file_path, autodetect_encoding=True)
    return loader.lazy_load()


def load_pdf(file_path: str | Path,
        password: str | bytes | None = None) -> Iterator[Document]:
    loader = PyPDFLoader(file_path, password=password)
    return loader.lazy_load() # Iterator[Document]


def load_docx(file_path: str | Path) -> Iterator[Document]:
    loader = Docx2txtLoader(file_path)
    return loader.lazy_load()
