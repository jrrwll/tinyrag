from datetime import datetime
from typing import Any

from sqlmodel import update, Session, select, func

from app.common.deps import open_session
from app.core.task.enums import AsyncTaskStatus, AsyncTaskType
from app.entities.task import AsyncTask


def page_and_count_tasks(
        session: Session, page_no: int, page_size: int,
        types: list[AsyncTaskType], workspace_id: int, tenant_id: int
) -> tuple[list[dict], int]: # type: ignore[type-arg]
    conditions = [
        AsyncTask.tenant_id == tenant_id,
        AsyncTask.workspace_id == workspace_id,
        AsyncTask.type.in_(types),
    ]

    count_statement = (
        select(func.count()).select_from(AsyncTask).where(*conditions)
    )
    count = session.exec(count_statement).one()

    offset = (page_no - 1) * page_size
    limit = page_size

    page_statement = (
        select(  # type: ignore[call-overload]
            AsyncTask.id,
            AsyncTask.created_at,
            AsyncTask.type,
            AsyncTask.ref_id,
            AsyncTask.status,
            AsyncTask.submitted_at,
            AsyncTask.completed_at,
            AsyncTask.progress,
        )
        .select_from(AsyncTask)
        .where(*conditions)
        .order_by(AsyncTask.submitted_at.desc())
        .offset(offset)
        .limit(limit)
    )
    entities = session.exec(page_statement).mappings().all()
    return [dict(i) for i in entities], count


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
