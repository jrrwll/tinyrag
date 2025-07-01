from fastapi import APIRouter, Request, Response
from fastapi.exceptions import RequestValidationError

from app.api import model, private, workflow
from app.common.config import settings
from app.common.error_code import BizException, ErrorCode

api_router = APIRouter()
api_router.include_router(model.router)
api_router.include_router(workflow.router)


if settings.IS_TEST_ENV:
    api_router.include_router(private.router)


# exception_handler
def exception_handler(_: Request, e: Exception) -> Response:
    if isinstance(e, RequestValidationError):
        exc = BizException.new(ErrorCode.request_validation_error, e.errors())
    elif isinstance(e, BizException):
        exc = e
    else:
        exc = BizException.unknown(e)
    return exc.to_response()
