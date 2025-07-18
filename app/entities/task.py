from datetime import datetime

from sqlmodel import Field, SQLModel

from app.core.task.enums import AsyncTaskStatus


class AsyncTask(SQLModel, table=True):

    __tablename__ = "async_task"

    id: str = Field(primary_key=True)
    updated_at: datetime

    name: str = Field(min_length=1, max_length=100)
    payload: str
    status: AsyncTaskStatus = AsyncTaskStatus.Pending

    submitted_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result: str | None = None
    progress: int = 0

