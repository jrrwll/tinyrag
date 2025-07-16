from pydantic import BaseModel
from datetime import datetime
from app.core.task.enums import AsyncTaskStatus
from app.entities.task import AsyncTask


class AsyncTaskPublic(BaseModel):
    name: str
    payload: str
    status: AsyncTaskStatus

    submitted_at: datetime | None = None
    completed_at: datetime | None = None
    result: str | None = None
    progress: int | None = None

    @staticmethod
    def new(entity: AsyncTask) -> "AsyncTaskPublic":
        return AsyncTaskPublic(**entity.model_dump())
