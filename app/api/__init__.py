from fastapi import APIRouter, Request, Response
from fastapi.exceptions import RequestValidationError

from app.api import private, model, workflow
from app.common.config import settings
from app.common.error_code import BizException, ErrorCode

api_router = APIRouter()
api_router.include_router(model.router)
api_router.include_router(workflow.router)


if settings.IS_TEST_ENV:
    api_router.include_router(private.router)


# exception_handler
def validation_exception_handler(_: Request,
        e: RequestValidationError) -> Response:
    exc = BizException.new(ErrorCode.request_validation_error, e.errors())
    return exc.to_response()


def biz_exception_handler(_: Request, exc: BizException) -> Response:
    return exc.to_response()


def exception_handler(_: Request, e: Exception) -> Response:
    exc = BizException.unknown(e)
    return exc.to_response()
