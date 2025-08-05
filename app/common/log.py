import logging
import os.path
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler

import pytz
from fastapi import Depends, Request
from fastapi.routing import APIRoute

from app.common.app_dispatch import request_id_var
from app.config import settings

logger = logging.getLogger(__name__)


def config_logging() -> None:
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
        handler.addFilter(_RequestIdFilter())

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

        def time_converter(seconds): # type: ignore[no-untyped-def]
            return datetime.fromtimestamp(seconds, tz=timezone).timetuple()

        for handler in logging.root.handlers:
            if handler.formatter:
                handler.formatter.converter = time_converter


class _RequestIdFilter(logging.Filter):

    def filter(self, record) -> bool: # type: ignore[no-untyped-def]
        record.requestId = request_id_var.get() if request_id_var.get() else ""
        return True


def _request_logger(request: Request) -> None:
    route: APIRoute = request.scope.get("route") # type: ignore[assignment]
    typ = request.scope.get("type", "")
    http_version = request.scope.get("http_version")
    request_str = f"{request.method} {route.path} {typ.upper()}/{http_version}"

    client = request.client
    if client:
        logger.info(f"{request_str} - {client.host}:{client.port}")
    else:
        logger.info(request_str)


LogDep = Depends(_request_logger)
