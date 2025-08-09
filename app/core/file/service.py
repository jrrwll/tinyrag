from app.config import settings
from app.core.file.api import FileUploadPublic
from app.core.file.file_type import allow_extensions


_upload_rule = FileUploadPublic(
    file_size_limit=settings.UPLOAD_FILE_SIZE_LIMIT,
    image_file_size_limit=settings.UPLOAD_IMAGE_FILE_SIZE_LIMIT,
    audio_file_size_limit=settings.UPLOAD_AUDIO_FILE_SIZE_LIMIT,
    video_file_size_limit=settings.UPLOAD_VIDEO_FILE_SIZE_LIMIT,
    allow_extensions=allow_extensions,
)


def get_upload_rule() -> FileUploadPublic:
    return _upload_rule
