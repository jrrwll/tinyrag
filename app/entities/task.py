from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from app.core.task.enums import AsyncTaskStatus


class AsyncTask(SQLModel, table=True):

    __tablename__ = "async_task"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(min_length=1, max_length=100)
    payload: str
    status: AsyncTaskStatus = AsyncTaskStatus.Pending

    submitted_at: datetime
    completed_at: datetime | None = None
    result: str | None = None
    progress: int = 0

