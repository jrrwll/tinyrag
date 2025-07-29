import logging
from typing import Any

from fastapi import APIRouter
from pydantic import EmailStr
from app.common.rq import AsyncTaskJob, RQManager
from app.config import settings
from app.core.user.email import generate_test_email, send_email
from app.util.api import ApiResult, PageResult

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
    return ApiResult.create(stat_dict)


@router.get("/queue-jobs", response_model=ApiResult[PageResult[Any]])
def queue_stat(page_no: int = settings.page_no_query,
        page_size: int = settings.page_size_query) -> Any:
    queue = RQManager().queue

    total = queue.count
    offset = (page_no - 1) * page_size

    if offset < total:
        jobs = queue.get_jobs(
            offset=offset, length=page_size)
        jobs = [AsyncTaskJob.dict(job) for job in jobs]
    else:
        jobs = []

    res = PageResult(
        page_no=page_no, page_size=page_size,
        total=total, items=jobs)

    return ApiResult.create(res)
