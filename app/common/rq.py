import logging
import threading
import time
from datetime import datetime
from typing import Any, Callable, Self

from redis import Redis
from rq import Queue, Worker
from rq.job import Job
from rq_scheduler import Scheduler

from app.config import settings

logger = logging.getLogger(__name__)


class RQManager:
    """singleton"""
    _instance: Self = None

    redis_conn: Redis
    queue: Queue
    scheduler: Scheduler
    worker_thread: threading.Thread |  None
    scheduler_thread: threading.Thread |  None
    shutdown_flag: threading.Event


    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.init()
        return cls._instance

    def submit_task(self, func: Callable[..., Any], *args, **kwargs) -> Job:
        return self.queue.enqueue(func, *args, **kwargs)

    def schedule_task(self, scheduled_time: datetime,
            func: Callable[..., Any], *args, **kwargs) -> Job:
        return self.scheduler.enqueue_at(scheduled_time, func, *args, **kwargs)

    def init(self):
        self.redis_conn = Redis.from_url(settings.RQ_REDIS_URL)
        self.queue = Queue(connection=self.redis_conn)

        self.scheduler = Scheduler(connection=self.redis_conn)
        self.worker_thread = None
        self.scheduler_thread = None
        self.shutdown_flag = threading.Event()

    def start_worker(self):

        def run_worker():
            worker = Worker(['default'], connection=self.redis_conn)
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

        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
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
