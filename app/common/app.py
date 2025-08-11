import logging

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from pydantic import ValidationError
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.base import api_router
from app.common.app_dispatch import add_request_vars
from app.common.error_code import BizException, ErrorCode
from app.common.log import config_logging
from app.config import settings
from app.util.model import extract_validation_error

config_logging("app", web_app=True)
logger = logging.getLogger(__name__)


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_PREFIX_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

app.include_router(api_router, prefix=settings.API_PREFIX_STR)
app.add_middleware(BaseHTTPMiddleware, dispatch=add_request_vars)


# app.add_exception_handler(Exception, exception_handler)
@app.exception_handler(Exception)
async def _exception_handler(_: Request, e: Exception) -> Response:
    logger.exception(f"unknown error: {e}")
    return BizException.unknown(e).to_response()


@app.exception_handler(RequestValidationError)
async def _request_validation_error_handler(
        _: Request, e: RequestValidationError) -> Response:
    return BizException.create(
        ErrorCode.request_validation_error, msg=str(e)
    ).to_response()


@app.exception_handler(HTTPException)
async def _http_exception_handler(_: Request, e: HTTPException) -> Response:
    logger.exception(f"http exception: {e}")
    return BizException(
        e.status_code, ErrorCode.request_error.name, msg=e.detail
    ).to_response()


@app.exception_handler(ValidationError)
async def _validation_error_handler(_: Request, e: ValidationError) -> Response:
    logger.exception(f"validation error: {e}")

    error_args = extract_validation_error(e)
    return BizException.create(
        ErrorCode.validation_error, **error_args
    ).to_response()


@app.exception_handler(BizException)
async def _http_exception_handler(_: Request, e: BizException) -> Response:
    return e.to_response()
