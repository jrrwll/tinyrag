from app.common.error_code import BizException, ErrorCode
from app.config import settings
from app.core.file.api import FileUploadPublic
from app.core.file.service.file_type import allow_extensions
from app.core.file.storage.base import get_storage_provider


def get_upload_rule() -> FileUploadPublic:
    return FileUploadPublic(
        file_size_limit=settings.UPLOAD_FILE_SIZE_LIMIT,
        image_file_size_limit=settings.UPLOAD_IMAGE_FILE_SIZE_LIMIT,
        audio_file_size_limit=settings.UPLOAD_AUDIO_FILE_SIZE_LIMIT,
        video_file_size_limit=settings.UPLOAD_VIDEO_FILE_SIZE_LIMIT,
        allow_extensions=allow_extensions,
    )


def get_storage_files(file_path: str) -> list[str]:
    storage_provider = get_storage_provider()
    if not storage_provider.exists(file_path):
        raise BizException.create(ErrorCode.remote_file_not_found, file_path)

    if not file_path.endswith("/"):
        return [file_path]

    files = storage_provider.list_files(
        file_path, recursive=True,
        limit=settings.STORAGE_LIST_FILE_MAX_COUNT)

    keys = [file.key for file in files if not file.is_dir]
    if not keys:
        raise BizException.create(
            ErrorCode.remote_file_not_found, file_path
        )
    return keys
