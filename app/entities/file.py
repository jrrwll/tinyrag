from datetime import datetime

from sqlmodel import Field, SQLModel


class File(SQLModel):
    id: str = Field(primary_key=True) # md5 char(32)
    created_at: datetime
    deleted: bool = False

    name: str
    size: int
    extension: str | None = None
    mime_type: str | None = None
