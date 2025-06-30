from enum import Enum, auto
from pathlib import Path

import configparser
from app.common.config import settings
from fastapi.responses import JSONResponse
from fastapi import Response
import os.path

_common_dir = Path(__file__).resolve().parent
_error_code_file = str(_common_dir / "error_code.ini")
_error_code_test_file = str(_common_dir / "error_code_test.ini")
_error_code_prod_file = str(_common_dir / "error_code_prod.ini")

_error_code_files = [_error_code_file]
if settings.IS_TEST_ENV and os.path.exists(_error_code_test_file):
    _error_code_files.append(_error_code_test_file)
elif not settings.IS_TEST_ENV and os.path.exists(_error_code_prod_file):
    _error_code_files.append(_error_code_prod_file)

_config = configparser.ConfigParser()
_config.read(_error_code_files)

_unknown_status_code = 500
try:
    _unknown_message = _config["500"]["unknown_error"]
except KeyError:
    raise Exception("unknown_error not found in error_code.ini")


class ErrorCode(Enum):
    unknown_error = auto()
    request_validation_error = auto()
    model_not_found = auto()
    workflow_not_found = auto()

    def get_status_code_and_message(self) -> (int, str):
        for status_code, kv in _config.items():
            message = kv.get(self.name)
            if message:
                return int(status_code), message
        return _unknown_status_code, _unknown_message


class BizException(Exception):
    error_code: str
    message: str
    status_code: int

    def __init__(self, error_code: str, message: str, status_code: int):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code

    @staticmethod
    def new(error_code: ErrorCode, *args):
        status_code, message = error_code.get_status_code_and_message()
        try:
            message = message.format(*args)
        except KeyError:
            pass

        return BizException(
            error_code=error_code.name,
            message=message,
            status_code=status_code)

    @staticmethod
    def unknown(exc: Exception) -> "BizException":
        message = _unknown_message
        if settings.IS_TEST_ENV:
            message = str(exc)

        return BizException(
            error_code=ErrorCode.unknown_error.name,
            message=message,
            status_code=_unknown_status_code)

    def to_response(self) -> Response:
        return JSONResponse(
            content={
                "error_code": self.error_code,
                "message": self.message,
            },
            status_code=self.status_code
        )
