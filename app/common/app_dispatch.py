import contextvars
import logging
import uuid

from fastapi import Request, Response

from corepy.collection import first_not_none

logger = logging.getLogger(__name__)

request_id_var = contextvars.ContextVar("request_id", default="")
lang_var = contextvars.ContextVar("lang_var", default="default")


# @app.middleware("http")
async def add_request_vars(request: Request,
        call_next) -> Response:  # type: ignore[no-untyped-def]
    # request_lang
    lang = first_not_none(
        request.headers, "X-Lang", "Accept-Language")
    if not lang:
        lang = "default"
    lang = lang.split(",")[0]
    lang_token = lang_var.set(lang)

    # request_id
    request_id = first_not_none(request.headers, "X-Request-ID")
    if not request_id:
        request_id = str(uuid.uuid4())
    request_id_token = request_id_var.set(request_id)

    try:
        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        request_id_var.reset(request_id_token)
        lang_var.reset(lang_token)
