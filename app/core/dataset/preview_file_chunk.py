from langchain_core.vectorstores import InMemoryVectorStore

from app.common.db import open_session
from app.common.error_code import BizException, ErrorCode
from app.core.dataset.api import PreviewChunk, PreviewChunkPublic
from app.core.dataset.process_rule import get_text_splitter, split_documents
from app.core.file.service import load_document_file
from app.core.model.default_model import get_default_model_provider
from app.core.model.enums import ModelType
from app.entities.file import File
from app.util.lang import take_limit


def preview_file_chunk(params: PreviewChunk) -> PreviewChunkPublic:
    file_id = params.file_id
    with open_session() as session:
        file = session.get(File, file_id)
        if not file:
            raise BizException.new(ErrorCode.file_not_found, file_id)

    docs = load_document_file(file)

    text_splitter = get_text_splitter(params.process_rule)
    all_splits = text_splitter.split_documents(take_limit(docs, 1))

    contents = [all_split.page_content for all_split in all_splits]
    return PreviewChunkPublic(content=contents)


def f():
    embedding = get_default_model_provider(ModelType.TextEmbedding)
    if not embedding:
        raise BizException.new(ErrorCode.default_model_not_set, ModelType.TextEmbedding)
    embeddings_model = embedding.embeddings_model

    vector_store = InMemoryVectorStore(embeddings_model)

    embeddings_model.embed_documents()
