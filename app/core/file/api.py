from datetime import datetime

from pydantic import BaseModel

from app.core.file.enums import FileType


class FilePublic(BaseModel):
    id: str
    created_at: datetime

    type: FileType
    name: str
    size: int
    mime_type: str


class FileUploadPublic(BaseModel):

    file_size_limit: int
    image_file_size_limit: int
    audio_file_size_limit: int
    video_file_size_limit: int

    allow_extensions: list[str]
