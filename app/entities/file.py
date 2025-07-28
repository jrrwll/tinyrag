from app.core.file.enums import FileType
from app.entities.base import LogTableBase, enum_field_info


class File(LogTableBase, table=True):

    type: FileType = enum_field_info(FileType)
    name: str
    size: int
    mime_type: str
