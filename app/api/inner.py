import logging
from datetime import datetime, timedelta
from typing import Annotated, Any
from uuid import uuid4

from fastapi import APIRouter
from pydantic import EmailStr
from rq.worker import Job

from app.common.deps import open_session
from app.config import settings
from app.core.task.enums import AsyncTaskType
from app.core.user.email import generate_test_email, send_email
from app.entities.task import AsyncTask
from app.tasks.base import RQManager, send_rq_scheduled_task
from corepy.api.result import ApiResult, PageResult
from corepy.datetime import isoformat_dict

router = APIRouter(tags=["inner"], prefix="/inner")

logger = logging.getLogger(__name__)


@router.get("/test-log")
def test_log() -> Any:
    logger.info(f"test log is: {logger}")


@router.get("/test-email")
def test_email(email_to: EmailStr) -> Any:
    subject, html_content = generate_test_email(email_to=email_to)
    send_email(
        email_to=email_to,
        subject=subject,
        html_content=html_content,
    )


@router.get("/queue-stat", response_model=ApiResult[Any])
def queue_stat() -> Any:
    rq_manager = RQManager()
    queue = rq_manager.queue

    stat_dict: dict[str, Any] = {
        "queue_name": queue.name,
        "queue_count": queue.count,
        "scheduler_pid": queue.scheduler_pid,
    }
    return ApiResult.ok(stat_dict)


@router.get("/queue-jobs", response_model=ApiResult[PageResult[Any]])
def queue_stat(page_no: Annotated[int, settings.page_no_query],
        page_size: Annotated[int, settings.page_size_query]) -> Any:
    queue = RQManager().queue

    total = queue.count
    offset = (page_no - 1) * page_size

    if offset < total:
        jobs = queue.get_jobs(
            offset=offset, length=page_size)
        jobs = [_to_job_dict(job) for job in jobs]
    else:
        jobs = []

    res = PageResult(
        page_no=page_no, page_size=page_size,
        total=total, items=jobs)

    return ApiResult.ok(res)


def _to_job_dict(job: Job) -> dict[str, Any]:
    job_dict = {
        "id": job.id,
        "description": job.description,
        "status": job.get_status(),
        "meta": job.meta,
        "func_name": job.func_name,
        "created_at": job.created_at,
        "enqueued_at": job.enqueued_at,
        "started_at": job.started_at,
        "ended_at": job.ended_at,
    }
    isoformat_dict(job_dict)
    return job_dict


@router.get("/test-scheduled-task")
def test_scheduled_task() -> Any:
    job_id = str(uuid4())
    with open_session() as session:
        entity = AsyncTask(
            id=job_id, type=AsyncTaskType.KnowledgeImport,
            workspace_id=1, tenant_id=1,
            ref_id=1, payload='{}')
        session.add(entity)
        session.commit()

    scheduled_time = datetime.now() + timedelta(seconds=5)
    logger.info(f"test scheduled task, start send: {job_id} {scheduled_time}")
    send_rq_scheduled_task(test_write_file, func_args=[], scheduled_time=scheduled_time, job_id=job_id)
    logger.info(f"test scheduled task, finish sent")
    return job_id


def test_write_file():
    logger.info(f"test writing file {datetime.now()}.txt")
