from datetime import datetime

from app.core.task.enums import AsyncTaskStatus, AsyncTaskType
from app.entities.base import LogTableBase, enum_field_info


class AsyncTask(LogTableBase, table=True):
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
