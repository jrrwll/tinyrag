from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.base import api_router
from app.common.app_dispatch import add_request_vars
from app.common.error_code import BizException, ErrorCode
from app.common.log import config_logging
from app.config import settings

config_logging("app")


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
async def exception_handler(_: Request, e: Exception) -> Response:
    if isinstance(e, RequestValidationError):
        exc = BizException.create(ErrorCode.request_validation_error,
                                  e.errors())
    elif isinstance(e, BizException):
        exc = e
    else:
        exc = BizException.unknown(e)
    return exc.to_response()


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, e: HTTPException) -> Response:
    return BizException.unknown(e).to_response()
