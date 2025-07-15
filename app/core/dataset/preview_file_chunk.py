from app.common.error_code import BizException, ErrorCode
from app.core.dataset.api import PreviewChunk, PreviewChunkPublic
from app.core.file.service import load_document_file

from app.core.model.default_model import get_default_model_provider
from app.core.model.enums import ModelType
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlmodel import Session

from app.common.config import settings
from app.common.db import engine
from app.entities.file import File


def preview_file_chunk(params: PreviewChunk) -> PreviewChunkPublic:
    file_id = params.file_id
    with Session(engine) as session:
        file = session.get(File, file_id)
        if not file:
            raise BizException.new(ErrorCode.file_not_found, file_id)

    docs = load_document_file(file, limit=1)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=params.chunk_size,
        chunk_overlap=params.chunk_overlap,
        separators=params.separators,
        add_start_index=True
    )
    all_splits = text_splitter.split_documents(docs)

    contents = [all_split.page_content for all_split in all_splits]
    return PreviewChunkPublic(content=contents)


def f():
    embedding = get_default_model_provider(ModelType.TextEmbedding)
    if not embedding:
        raise BizException.new(ErrorCode.default_model_not_set, ModelType.TextEmbedding)
    embeddings_model = embedding.embeddings_model

    vector_store = InMemoryVectorStore(embeddings_model)

    embeddings_model.embed_documents()
