from datetime import datetime

from sqlalchemy.orm import declared_attr
from sqlmodel import Field, SQLModel

from app.core.task.enums import AsyncTaskStatus, AsyncTaskType
from app.entities.base import enum_field_info
from corepy.text import camel_to_snake


class AsyncTask(SQLModel, table=True):
    id: str = Field(primary_key=True)
    created_at: datetime

    tenant_id: int
    workspace_id: int
    type: AsyncTaskType = enum_field_info(AsyncTaskType)
    ref_id: str | None = None
    payload: str | None = None
    status: AsyncTaskStatus = enum_field_info(
        AsyncTaskStatus, AsyncTaskStatus.Pending)

    submitted_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result: str | None = None
    progress: int = 0

    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:
        return camel_to_snake(cls.__name__)

