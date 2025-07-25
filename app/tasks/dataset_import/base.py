from pydantic import BaseModel

from app.core.file.enums import FileType
from app.core.rag.enums import DocumentSourceType


class FileTaskParams(BaseModel):
    file_path: str
    file_type: FileType
    source_info: str
    source_type: DocumentSourceType
