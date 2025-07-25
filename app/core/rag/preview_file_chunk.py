from langchain_core.vectorstores import InMemoryVectorStore

from app.common.db import open_session
from app.common.error_code import BizException, ErrorCode
from app.core.file.enums import FileType
from app.core.file.service.upload import get_file_path
from app.core.model.default_model import get_default_model_provider
from app.core.model.enums import ModelType
from app.core.rag.api import PreviewChunk, PreviewChunkPublic
from app.core.rag.text_process.base import get_text_processor
from app.entities.file import File
from app.util.collection import take_limit


def preview_file_chunk(params: PreviewChunk) -> PreviewChunkPublic:
    file_id = params.file_id
    with open_session() as session:
        file = session.get(File, file_id)
        if not file:
            raise BizException.create(ErrorCode.file_not_found, file_id)

    if not FileType.is_document(file.type):
        raise BizException.create(ErrorCode.file_not_a_document, file.typ)

    file_path = get_file_path(file.id)

    text_processor = get_text_processor(params.process_rule)
    docs = text_processor.load_documents(file_path, file.type)

    all_splits = text_processor.split_documents(take_limit(docs, 1))

    contents = [all_split.content for all_split in all_splits]
    return PreviewChunkPublic(content=contents)


def f():
    embedding = get_default_model_provider(ModelType.TextEmbedding)
    if not embedding:
        raise BizException.create(ErrorCode.default_model_not_set, ModelType.TextEmbedding)
    embeddings_model = embedding.embeddings_model

    vector_store = InMemoryVectorStore(embeddings_model)

    embeddings_model.embed_documents()
