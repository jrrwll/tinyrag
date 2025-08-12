from datetime import datetime

from pydantic import BaseModel

from app.core.task.enums import AsyncTaskStatus, AsyncTaskType
from app.entities.task import AsyncTask


class SimpleAsyncTaskPublic(BaseModel):
    id: str
    type: AsyncTaskType
    ref_id: str | None = None
    ref_name: str | None = None
    status: AsyncTaskStatus

    submitted_at: datetime
    completed_at: datetime | None = None
    progress: int | None = None


class AsyncTaskPublic(SimpleAsyncTaskPublic):
    payload: str | None = None

    started_at: datetime | None = None
    result: str | None = None

    @staticmethod
    def create(entity: AsyncTask) -> "AsyncTaskPublic":
        return AsyncTaskPublic(**entity.model_dump())
