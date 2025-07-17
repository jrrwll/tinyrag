from datetime import datetime

from sqlmodel import Field

from app.core.task.enums import AsyncTaskStatus
from app.entities.base import TableUUIDBase


class AsyncTask(TableUUIDBase, table=True):

    __tablename__ = "async_task"

    name: str = Field(min_length=1, max_length=100)
    payload: str
    status: AsyncTaskStatus = AsyncTaskStatus.Pending

    submitted_at: datetime
    completed_at: datetime | None = None
    result: str | None = None
    progress: int = 0
