from rq import SimpleWorker

from app.config import settings
from app.tasks.base import AsyncTaskJob, RQManager

# test mode, rq worker & scheduler entrypoint
if __name__ == '__main__':
    rq_manager = RQManager()

    # macOS/Windows only supports spawn rather than fork
    # so just use same process for test purpose
    worker = SimpleWorker(
        queues=[rq_manager.queue], connection=rq_manager.connection,
        job_class=AsyncTaskJob)
    worker.work(with_scheduler=True, logging_level=settings.LOG_LEVEL)
