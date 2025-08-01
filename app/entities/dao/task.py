from uuid import uuid4

from sqlmodel import Session

from app.core.task.enums import AsyncTaskStatus, AsyncTaskType
from app.entities.task import AsyncTask


def create_async_task(session: Session, task_type: AsyncTaskType, ref_id: int,
        payload: str, status: AsyncTaskStatus | None = None) -> AsyncTask:
    task_id = str(uuid4())

    entity = AsyncTask(
        id=task_id, type=task_type,
        ref_id=ref_id, payload=payload)
    if status:
        entity.status = status

    session.add(entity)
    session.commit()
    return entity
