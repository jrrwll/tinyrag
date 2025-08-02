# mypy: disable-error-code="no-untyped-def,no-any-return,union-attr,no-untyped-call,import-untyped"
import logging
import threading
import time
from datetime import datetime
from typing import Any, Callable, Self
import traceback

from redis import Redis
from rq import Queue, Worker
from rq.job import Job
from rq_scheduler import Scheduler

from app.common.constants import APP_NAME
from app.common.log import request_id_var
from app.config import settings
from app.core.task.service import update_task_status
from app.core.task.enums import AsyncTaskStatus
from app.util.datetime import isoformat_dict
from app.util.model import dump_json

logger = logging.getLogger(__name__)


class AsyncTaskJob(Job):

    @classmethod
    def dict(cls, job: Job) -> dict[str, Any]:
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

    def _execute(self) -> Any:
        request_id = self.meta.get("request_id")
        request_id_var.set(request_id if request_id else "")

        task_id = self.id
        if not update_task_status(
                task_id, AsyncTaskStatus.Pending, AsyncTaskStatus.Started):
            logger.warning(f"async_task={task_id}, failed to update status Pending -> Started")
            return None

        res, ex_str = None, None
        try:
            res = super()._execute()
        except Exception:
            ex_str = traceback.format_exc()
            logger.error(f"async_task={task_id}, failed with exception: {ex_str}")

        res_str = dump_json(res) if res else None

        if not ex_str:
            if not update_task_status(task_id, AsyncTaskStatus.Started,
                AsyncTaskStatus.Success, res_str):
                logger.warning(f"async_task={task_id}, failed to update status Started -> Success")
        else:
            if not update_task_status(task_id, AsyncTaskStatus.Started,
                AsyncTaskStatus.Failure, ex_str):
                logger.warning(f"async_task={task_id}, failed to update status Started -> Failure")

        return res


class RQManager:
    """singleton"""
    _instance: Self = None # type: ignore[assignment]

    connection: Redis
    queue: Queue

    # only for test env
    scheduler: Scheduler | None
    worker_thread: threading.Thread | None
    scheduler_thread: threading.Thread | None
    shutdown_flag: threading.Event | None

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
        self.queue = Queue(name=APP_NAME, connection=self.connection)

        if settings.IS_TEST_ENV:
            self.scheduler = Scheduler(connection=self.connection)
            self.worker_thread = None
            self.scheduler_thread = None
            self.shutdown_flag = threading.Event()

    def start_worker(self):

        def run_worker():
            worker = Worker([self.queue], connection=self.connection,
                            job_class=AsyncTaskJob)
            logger.info("🚀 RQ Worker started in thread mode")
            while not self.shutdown_flag.is_set():
                try:
                    worker.work(burst=True, with_scheduler=False)
                except Exception as e:
                    logger.error(f"RQ  Worker error: {e}")
                time.sleep(1)
            logger.info("🚀 RQ Worker exited")

        self.worker_thread = threading.Thread(target=run_worker, daemon=True)
        self.worker_thread.start()

    def start_scheduler(self):

        def run_scheduler():
            logger.info("⏰ RQ Scheduler started")
            while not self.shutdown_flag.is_set():
                try:
                    self.scheduler.run(burst=True)
                except Exception as e:
                    logger.error(f"RQ Scheduler error: {e}")
                time.sleep(1)
            logger.info("⏰ RQ Scheduler exited")

        self.scheduler_thread = threading.Thread(target=run_scheduler,
                                                 daemon=True)
        self.scheduler_thread.start()

    def stop_all(self):
        logger.info("🛑 Stopping RQ components...")
        self.shutdown_flag.set()

        if self.scheduler_thread and self.scheduler_thread.is_alive():
            logger.info("Stopping scheduler...")
            self.scheduler_thread.join(timeout=5.0)

        if self.worker_thread and self.worker_thread.is_alive():
            logger.info("Stopping worker...")
            self.worker_thread.join(timeout=5.0)

        logger.info("🛑 All RQ components stopped")


# @app.on_event("startup")
async def startup_rq_manager():
    rq_manager = RQManager()
    rq_manager.start_worker()
    rq_manager.start_scheduler()
    logger.info("🏁 RQ Manager started with worker and scheduler")


# @app.on_event("shutdown")
async def shutdown_rq_manager():
    RQManager().stop_all()


def send_rq_task(job_id: str, func: Callable[..., Any], *args, **kwargs):
    RQManager().submit_task(func, *args, **kwargs, job_id=job_id)


def send_rq_scheduled_task(job_id: str, scheduled_time: datetime,
        func: Callable[..., Any], *args, **kwargs):
    RQManager().schedule_task(
        scheduled_time, func, *args, **kwargs,
        job_id=job_id)


def main() -> None:
    from rq.worker import DequeueStrategy

    dequeue_strategy = DequeueStrategy.DEFAULT
    if settings.RQ_DEQUEUE_STRATEGY == DequeueStrategy.ROUND_ROBIN:
        dequeue_strategy = DequeueStrategy.ROUND_ROBIN
    elif settings.RQ_DEQUEUE_STRATEGY == DequeueStrategy.RANDOM:
        dequeue_strategy = DequeueStrategy.RANDOM

    rq_manager = RQManager()
    worker = Worker([rq_manager.queue], connection=rq_manager.connection,
                    job_class=AsyncTaskJob)
    # block forever
    worker.work(with_scheduler=True, logging_level=settings.LOG_LEVEL,
                dequeue_strategy=dequeue_strategy)
