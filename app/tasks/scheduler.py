from rq_scheduler import Scheduler

from app.common.log import config_logging
from app.tasks.base import AsyncTaskJob, RQManager

# production mode, rq scheduler entrypoint
if __name__ == '__main__':
    config_logging("scheduler")

    rq_manager = RQManager()

    scheduler = Scheduler(
        queue=rq_manager.queue, connection=rq_manager.connection,
        job_class=AsyncTaskJob,
    )
    scheduler.run()
