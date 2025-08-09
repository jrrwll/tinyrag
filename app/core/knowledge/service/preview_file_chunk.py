from app.common.deps import open_session
from app.common.error_code import BizException, ErrorCode
from app.config import settings
from app.core.file.file_type import detect_file_type
from app.core.file.upload import get_file_path
from app.core.knowledge.api import DocumentPreviewChunk, \
    DocumentPreviewChunkPublic
from app.core.knowledge.text_process.base import get_text_processor
from app.core.storage.default_storage import get_default_storage
from app.core.storage.file import download_storage_file
from app.core.storage.provider.base import StorageProviderFactory
from app.entities.dao.file import get_files
from app.util.collection import take_limit


def preview_file_chunk(
        params: DocumentPreviewChunk, tenant_id: int
) -> DocumentPreviewChunkPublic:
    file_id = params.file_id
    storage_id = params.storage_id
    storage_file_path = params.storage_file_path

    if file_id:
        with open_session() as session:
            file = get_files(session, [file_id], tenant_id).get(file_id)
            if not file:
                raise BizException.create(ErrorCode.file_not_found)
        file_path = get_file_path(file.id)
        file_type = file.type
    else:
        with open_session() as session:
            storage = get_default_storage(session, storage_id, tenant_id)

        storage_provider = StorageProviderFactory.create_storage(storage)
        metadata = storage_provider.metadata(storage_file_path)
        if not metadata:
            raise BizException.create(ErrorCode.storage_file_not_found)
        elif metadata.is_dir:
            raise BizException.create(ErrorCode.storage_file_not_file)
        elif metadata.size > settings.STORAGE_FILE_MAX_SIZE << 20:
            raise BizException.create(ErrorCode.storage_file_too_large)

        file_path = download_storage_file(storage_file_path, storage_provider)
        # TODO send mq delay msg to delete file

        file_type = detect_file_type(file_path)
        if file_type:
            file_type, _ = file_type

    if not file_type:
        raise BizException.create(ErrorCode.file_type_not_supported)
    if not file_type.is_document():
        raise BizException.create(ErrorCode.file_not_a_document, file_type=file_type)

    text_processor = get_text_processor(params.process_rule)
    docs = text_processor.load_documents(file_path, file_type)

    all_splits = text_processor.split_documents(take_limit(docs, 1))

    contents = [all_split.content for all_split in all_splits]
    return DocumentPreviewChunkPublic(content=contents)
