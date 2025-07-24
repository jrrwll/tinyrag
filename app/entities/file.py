from datetime import datetime

from sqlmodel import Field, SQLModel

from app.core.file.enums import FileType
from app.entities.base import enum_field_info


class File(SQLModel, table=True):
    id: str = Field(primary_key=True) # md5 char(32)
    created_at: datetime
    deleted: bool = False

    type: FileType = enum_field_info(FileType)
    name: str
    size: int
    mime_type: str
