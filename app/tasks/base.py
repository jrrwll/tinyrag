# mypy: disable-error-code="no-untyped-def,no-any-return,union-attr,no-untyped-call,import-untyped"
import logging
import traceback
from contextlib import AbstractContextManager
from datetime import datetime
from typing import Any, Callable, Self

from redis import Redis
from rq import Queue
from rq.job import Job
from rq.serializers import JSONSerializer

from app.common.constants import APP_NAME
from app.common.app_dispatch import request_id_var
from app.config import settings
from app.core.task.enums import AsyncTaskStatus
from app.core.task.service import update_task_status

logger = logging.getLogger(__name__)


class AsyncTaskContextManager(AbstractContextManager):

    def __init__(self, job: Job):
        self.job = job
        self.early_exit = False

    def __enter__(self) -> Self:
        request_id = self.job.meta.get("request_id", "")
        self.request_id_token = request_id_var.set(request_id)

        task_id = self.job.id
        if not update_task_status(
                task_id, AsyncTaskStatus.Pending, AsyncTaskStatus.Started):
            logger.warning(
                f"async_task={task_id}, failed to update status Pending -> Started")
            self.early_exit = True
        return self

    def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: object | None,
    ) -> None:
        if self.early_exit:
            return

        res_str = None
        if exc_type:
            status = AsyncTaskStatus.Failure
            res_str = "".join(
                traceback.format_exception(exc_type, exc_val, exc_tb))
        else:
            status = AsyncTaskStatus.Success
            return_value = self.job.return_value()
            if return_value:
                res_str = str(return_value)

        task_id = self.job.id
        try:
            if not update_task_status(
                    task_id, AsyncTaskStatus.Started,
                    status, res_str):
                logger.warning(
                    f"async_task={task_id}, failed to update status Started -> {status}")
        finally:
            if self.request_id_token:
                request_id_var.reset(self.request_id_token)


class AsyncTaskJob(Job):

    def _execute(self) -> Any:
        with AsyncTaskContextManager(self) as manager:
            if manager.early_exit:
                return False
            return super()._execute()


class RQManager:
    """singleton"""
    _instance: Self = None  # type: ignore[assignment]

    connection: Redis
    queue: Queue

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.init()
        return cls._instance

    def submit_task(self, func: Callable[..., Any], *args, **kwargs) -> Job:
        meta = {"request_id": request_id_var.get()}
        return self.queue.enqueue(func, meta=meta, *args, **kwargs)

    def schedule_task(self, scheduled_time: datetime,
            func: Callable[..., Any], *args, **kwargs) -> Job:
        return self.queue.enqueue_at(scheduled_time, func, *args, **kwargs)

    def init(self):
        self.connection = Redis.from_url(settings.RQ_REDIS_URL)
        self.queue = Queue(name=APP_NAME, connection=self.connection,
                           serializer=JSONSerializer)


def send_rq_task(job_id: str, func: Callable[..., Any], *args, **kwargs):
    RQManager().submit_task(func, *args, **kwargs, job_id=job_id)


def send_rq_scheduled_task(job_id: str, scheduled_time: datetime,
        func: Callable[..., Any], *args, **kwargs):
    RQManager().schedule_task(
        scheduled_time, func, *args, **kwargs,
        job_id=job_id)
