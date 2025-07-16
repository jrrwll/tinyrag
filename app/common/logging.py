import contextvars
import sys
import uuid
from logging.handlers import RotatingFileHandler
from app.config import settings
import os.path
import logging
from fastapi import Request, Response
from datetime import datetime
import pytz


request_id_var = contextvars.ContextVar("request_id")


# @app.middleware("http")
async def add_request_id(request: Request, call_next) -> Response:
    request_id = request.headers.get("request_id")
    if not request_id:
        request_id = str(uuid.uuid4())

    request_id_var.set(request_id)

    response = await call_next(request)

    response.headers["request_id"] = request_id
    return response


def config_logging():
    log_handlers: list[logging.Handler] = []

    log_file = settings.LOG_FILE
    if log_file:
        log_dir = os.path.dirname(log_file)
        os.makedirs(log_dir, exist_ok=True)
        log_handlers.append(
            RotatingFileHandler(
                filename=log_file,
                maxBytes=settings.LOG_FILE_MAX_SIZE * 1024 * 1024,
                backupCount=settings.LOG_FILE_BACKUP_COUNT,
            )
        )

    # console log
    log_handlers.append(logging.StreamHandler(sys.stdout))
    # add requestId
    for handler in log_handlers:
        handler.addFilter(RequestIdFilter())

    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format=settings.LOG_FORMAT,
        datefmt=settings.LOG_DATEFORMAT,
        handlers=log_handlers,
        force=True,
    )

    log_tz = settings.LOG_TZ
    if log_tz:
        timezone = pytz.timezone(log_tz)

        def time_converter(seconds):
            return datetime.fromtimestamp(seconds, tz=timezone).timetuple()

        for handler in logging.root.handlers:
            if handler.formatter:
                handler.formatter.converter = time_converter


class RequestIdFilter(logging.Filter):
    # This is a logging filter that makes the request ID available for use in
    # the logging format. Note that we're checking if we're in a request
    # context, as we may want to log things before Flask is fully loaded.
    def filter(self, record):
        record.requestId = request_id_var.get() if request_id_var.get() else ""
        return True
