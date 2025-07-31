from datetime import datetime

from sqlmodel import Field, SQLModel

from app.core.file.enums import FileType
from app.entities.base import enum_field_info


class File(SQLModel, table=True):
    id: str = Field(primary_key=True)
    created_at: datetime

    tenant_id: int
    workspace_id: int
    type: FileType = enum_field_info(FileType)
    name: str
    size: int
    mime_type: str
