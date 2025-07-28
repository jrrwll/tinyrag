# from datetime import datetime
# import threading
#
# import pytz
# from celery import Celery
# from celery.signals import task_postrun, task_prerun
#
# from app.common.db import open_session
# from app.config import settings
# from app.entities.task import AsyncTask, AsyncTaskStatus
#
# _celery_main = 'tasks'
#
# # beat
# _beat_schedule = {
# }
#
# def init_celery_app() -> Celery:
#     app = Celery(
#         main=_celery_main,
#         broker=settings.CELERY_BROKER_URL,
#         backend=settings.CELERY_BACKEND,
#         task_ignore_result=True,
#     )
#
#     broker_transport_options = {}
#     if settings.CELERY_SENTINEL_MASTER_NAME:
#         broker_transport_options = {
#             "master_name": settings.CELERY_SENTINEL_MASTER_NAME,
#             "sentinel_kwargs": {
#                 "socket_timeout": settings.CELERY_SENTINEL_SOCKET_TIMEOUT,
#             },
#         }
#
#     app.conf.update(
#         result_backend=settings.CELERY_RESULT_BACKEND,
#         broker_transport_options=broker_transport_options,
#         broker_connection_retry_on_startup=True,
#         worker_log_format=settings.LOG_FORMAT,
#         worker_task_log_format=settings.LOG_FORMAT,
#         worker_hijack_root_logger=False,
#         worker_logfile=settings.LOG_FILE,
#         timezone=pytz.timezone(settings.LOG_TZ or "UTC"),
#     )
#
#     ssl_options = {
#         "ssl_cert_reqs": None,
#         "ssl_ca_certs": None,
#         "ssl_certfile": None,
#         "ssl_keyfile": None,
#     }
#     if settings.BROKER_USE_SSL:
#         app.conf.update(
#             broker_use_ssl=ssl_options,
#         )
#
#     app.set_default()
#
#
#     imports = list(_beat_schedule.keys())
#     app.conf.update(beat_schedule=_beat_schedule, imports=imports)
#
#     return app
#
# celery = init_celery_app()
#
#
# def send_celery_task(task_id: str, task_name: str, *args, **kwargs) -> None:
#     celery.send_task(
#         f"{_celery_main}.{task_name}",
#         task_id=task_id,
#         args=args,
#         kwargs=kwargs
#     )
#
#
# @task_prerun.connect
# def task_started_handler(task_id: str, **kwargs):
#     with open_session() as session:
#         entity = session.get(AsyncTask, task_id)
#         if not entity:
#             return
#
#         entity.status = AsyncTaskStatus.Started
#         entity.submitted_at = datetime.now()
#         session.commit()
#
#
# @task_postrun.connect
# def task_completed_handler(task_id, **kwargs):
#     result = kwargs.get("retval")
#     exception = kwargs.get("exception")
#
#     with open_session() as session:
#         entity = session.get(AsyncTask, task_id)
#         if not entity:
#             return
#
#         if exception:
#             entity.status = AsyncTaskStatus.Failure
#             entity.result = str(exception)
#         else:
#             entity.status = AsyncTaskStatus.Success
#             entity.result = str(result)
#
#         entity.completed_at = datetime.now()
#         entity.progress = 100
#         session.add(entity)
#         session.commit()
#
#
# def start_embedded_servers():
#     worker_thread = threading.Thread(target=_run_worker, daemon=True)
#     worker_thread.start()
#
#     if _beat_schedule:
#         beat_thread = threading.Thread(target=_run_beat, daemon=True)
#         beat_thread.start()
#
#
# def _run_worker():
#     celery.worker_main([
#         'worker',
#         '--loglevel=info',
#         '--pool=solo',
#         '--concurrency=1'
#     ])
#
#
# def _run_beat():
#     from celery.apps.beat import Beat
#
#     beat = Beat(app=celery)
#     beat.run()
#
# """
# # task define demo
#
# send_celery_task(task_id, knowledge_import_task.__name__,
#                  task_id, task_params_json)
#
# @celery.task(queue="knowledge", bind=True, track_started=True)
# def knowledge_import_task(task_id: str, task_params_json: bytes):
#     pass
# """
