import os
import time
from multiprocessing import Process
from typing import Iterable

from redis import ConnectionPool
from rq import Queue, Worker
from rq.job import Job
from rq.serializers import DefaultSerializer, Serializer, JSONSerializer
from rq.worker import BaseWorker
from rq.worker_pool import WorkerPool

from app.common.log import config_logging
from app.config import settings
from app.tasks.base import AsyncTaskJob, RQManager


def run_worker_without_scheduler(
        worker_name: str,
        queue_names: Iterable[str],
        connection_class,
        connection_pool_class,
        connection_pool_kwargs: dict,
        worker_class: type[BaseWorker] = Worker,
        serializer: Serializer = DefaultSerializer,
        job_class: type[Job] = Job,
        queue_class: type[Queue] = Queue,
        burst: bool = True,
        logging_level: str = 'INFO',
        _sleep: int = 0,
):
    connection = connection_class(
        connection_pool=ConnectionPool(connection_class=connection_pool_class,
                                       **connection_pool_kwargs)
    )
    queues = [queue_class(name, connection=connection) for name in queue_names]
    worker = worker_class(
        queues,
        name=worker_name,
        connection=connection,
        serializer=serializer,
        job_class=job_class,
        queue_class=queue_class,
    )
    worker.log.info('Starting worker started with PID %s', os.getpid())
    time.sleep(_sleep)
    worker.work(burst=burst, logging_level=logging_level)


# run worker without scheduler
class NoSchedulerWorkerPool(WorkerPool):

    def get_worker_process(
            self,
            name: str,
            burst: bool,
            _sleep: float = 0,
            logging_level: str = 'INFO',
    ) -> Process:
        return Process(
            target=run_worker_without_scheduler,
            args=(name, self._queue_names, self._connection_class,
                  self._pool_class, self._pool_kwargs),
            kwargs={
                '_sleep': _sleep,
                'burst': burst,
                'logging_level': logging_level,
                'worker_class': self.worker_class,
                'job_class': self.job_class,
                'serializer': self.serializer,
            },
            name=f'Worker {name} (WorkerPool {self.name})',
        )


# production mode, rq worker entrypoint
if __name__ == '__main__':
    config_logging("worker")

    rq_manager = RQManager()

    pool = NoSchedulerWorkerPool(
        queues=[rq_manager.queue], connection=rq_manager.connection,
        job_class=AsyncTaskJob, serializer=JSONSerializer,
        num_workers=settings.RQ_WORKERS, )
    pool.start(logging_level=settings.LOG_LEVEL)
