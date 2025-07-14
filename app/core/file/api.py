from datetime import datetime

from pydantic import BaseModel


class FilePublic(BaseModel):
    id: str
    created_at: datetime

    name: str
    size: int
    extension: str | None = None
    mime_type: str | None = None
