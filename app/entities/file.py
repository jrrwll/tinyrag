from datetime import datetime

from sqlmodel import Field

from app.core.file.enums import FileType
from app.entities.base import LogTableBase, enum_field_info


class File(LogTableBase, table=True):
    id: str = Field(primary_key=True)
    updated_at: datetime
    deleted: bool = False

    tenant_id: int
    workspace_id: int
    type: FileType = enum_field_info(FileType)
    name: str
    size: int
    mime_type: str
