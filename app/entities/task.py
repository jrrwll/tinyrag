from datetime import datetime

from sqlmodel import Field, SQLModel

from app.core.task.enums import AsyncTaskStatus, AsyncTaskType
from app.entities.base import enum_field_info


class AsyncTask(SQLModel, table=True):
    id: str = Field(primary_key=True)
    created_at: datetime

    tenant_id: int
    type: AsyncTaskType = enum_field_info(AsyncTaskType)
    ref_id: str | None = None
    payload: str
    status: AsyncTaskStatus = enum_field_info(
        AsyncTaskStatus, AsyncTaskStatus.Pending)

    submitted_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result: str | None = None
    progress: int = 0
