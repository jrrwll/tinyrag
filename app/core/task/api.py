from datetime import datetime

from pydantic import BaseModel

from app.core.task.enums import AsyncTaskStatus, AsyncTaskType
from app.entities.task import AsyncTask


class AsyncTaskPublic(BaseModel):
    id: str
    type: AsyncTaskType
    ref_id: str | None = None
    payload: str
    status: AsyncTaskStatus

    submitted_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result: str | None = None
    progress: int | None = None

    @staticmethod
    def new(entity: AsyncTask) -> "AsyncTaskPublic":
        return AsyncTaskPublic(**entity.model_dump())
