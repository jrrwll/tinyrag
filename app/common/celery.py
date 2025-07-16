from datetime import datetime
from typing import Any

from celery import Celery
from celery.signals import after_setup_task_logger, task_prerun, task_postrun

from app.common.db import open_session
from app.config import settings
import pytz

from app.entities.task import AsyncTask, AsyncTaskStatus

_celery_main = 'tasks'

def init_celery_app() -> Celery:
    app = Celery(
        main=_celery_main,
        broker=settings.CELERY_BROKER_URL,
        backend=settings.CELERY_BACKEND,
        task_ignore_result=True,
    )

    broker_transport_options = {}
    if settings.CELERY_SENTINEL_MASTER_NAME:
        broker_transport_options = {
            "master_name": settings.CELERY_SENTINEL_MASTER_NAME,
            "sentinel_kwargs": {
                "socket_timeout": settings.CELERY_SENTINEL_SOCKET_TIMEOUT,
            },
        }

    app.conf.update(
        result_backend=settings.CELERY_RESULT_BACKEND,
        broker_transport_options=broker_transport_options,
        broker_connection_retry_on_startup=True,
        worker_log_format=settings.LOG_FORMAT,
        worker_task_log_format=settings.LOG_FORMAT,
        worker_hijack_root_logger=False,
        worker_logfile=settings.LOG_FILE,
        timezone=pytz.timezone(settings.LOG_TZ or "UTC"),
    )

    ssl_options = {
        "ssl_cert_reqs": None,
        "ssl_ca_certs": None,
        "ssl_certfile": None,
        "ssl_keyfile": None,
    }
    if settings.BROKER_USE_SSL:
        app.conf.update(
            broker_use_ssl=ssl_options,
        )

    app.set_default()

    # beat
    beat_schedule = {
    }
    imports = list(beat_schedule.keys())
    app.conf.update(beat_schedule=beat_schedule, imports=imports)

    return app

celery = init_celery_app()


def send_celery_task(task_id: str, task_name: str, *args, **kwargs) -> None:
    celery.send_task(
        f"{_celery_main}.{task_name}",
        task_id=task_id,
        args=args,
        kwargs=kwargs
    )


@task_prerun.connect
def task_started_handler(task_id: str):
    """任务开始运行时更新状态"""
    with open_session() as session:
        entity = session.get(AsyncTask, task_id)
        if not entity:
            return

        entity.status = AsyncTaskStatus.Started
        entity.submitted_at = datetime.now()
        session.commit()


@task_postrun.connect
def task_completed_handler(task_id, **kwargs):
    result = kwargs.get("retval")
    exception = kwargs.get("exception")

    with open_session() as session:
        entity = session.get(AsyncTask, task_id)
        if not entity:
            return

        if exception:
            entity.status = AsyncTaskStatus.Failure
            entity.result = str(exception)
        else:
            entity.status = AsyncTaskStatus.Success
            entity.result = str(result)

        entity.completed_at = datetime.now()
        entity.progress = 100
        session.add(entity)
        session.commit()
