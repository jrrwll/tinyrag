from datetime import datetime
from typing import Any

from sqlmodel import update

from app.common.db import open_session
from app.core.task.enums import AsyncTaskStatus
from app.entities.task import AsyncTask


def update_task_status(task_id: str, expect_status: AsyncTaskStatus,
        target_status: AsyncTaskStatus, result: str | None = None) -> bool:
    values: dict[str, Any] = {
        "status": target_status,
    }
    if result:
        values["result"] = result

    if (target_status == AsyncTaskStatus.Success
            or target_status == AsyncTaskStatus.Failure):
        values["completed_at"] = datetime.now()
        values["progress"] = 100
    elif target_status == AsyncTaskStatus.Started:
        values["started_at"] = datetime.now()

    with open_session() as session:
        update_sql = update(AsyncTask).where(
            AsyncTask.id == task_id,
            AsyncTask.status == expect_status,
        ).values(values)
        res = session.exec(update_sql)
        session.commit()
        return res.rowcount > 0


def update_task_progress(task_id: str, progress: int) -> bool:
    with open_session() as session:
        update_sql = update(AsyncTask).where(
            AsyncTask.id == task_id,
            AsyncTask.status == AsyncTaskStatus.Started,
        ).values(progress=progress)
        res = session.exec(update_sql)
        session.commit()
        return res.rowcount > 0
