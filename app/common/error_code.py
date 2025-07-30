import configparser
import os.path
from enum import Enum, auto
from pathlib import Path

from fastapi import Response, HTTPException
from fastapi.responses import JSONResponse

from app.config import settings

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
    ok = auto()
    unknown_error = auto()
    request_validation_error = auto()
    request_validation_error_detail = auto()

    # auth
    email_or_password_incorrect = auto()
    same_new_password = auto()
    login_user_inactive = auto()
    user_inactive = auto()
    user_email_already_exists = auto()
    super_user_cannot_delete = auto()
    invalid_email_domain = auto()
    login_user_not_found = auto()
    user_not_found = auto()
    user_email_not_found = auto()
    invalid_token = auto()
    invalid_credentials = auto()
    insufficient_permissions = auto()
    permission_already_granted = auto()
    permission_not_granted = auto()

    # feature
    workspace_not_found = auto()
    workspace_name_already_exists = auto()

    model_not_found = auto()
    model_type_not_supported = auto()
    model_provider_not_supported = auto()
    default_model_not_set = auto()
    need_specific_type_model = auto()
    model_name_not_supported = auto()
    model_is_set_in_default = auto()

    vector_store_not_found = auto()
    vector_store_is_set_in_default = auto()

    workflow_not_found = auto()
    workflow_run_not_found = auto()
    related_workflow_not_found = auto()

    node_not_found = auto()

    code_main_func_undefined = auto()
    code_eval_error = auto()

    file_type_not_supported = auto()
    file_not_found = auto()
    file_not_a_document = auto()
    storage_file_not_found = auto()

    knowledge_not_found = auto()
    knowledge_conversation_not_found = auto()

    def get_status_code_and_message(self) -> tuple[int, str]:
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
    def create(error_code: ErrorCode, *args) -> "BizException":  # type: ignore[no-untyped-def]
        status_code, message = error_code.get_status_code_and_message()
        try:
            message = message.format(*args)
        except KeyError:
            pass

        return BizException(
            error_code=error_code.name, message=message, status_code=status_code
        )

    @staticmethod
    def unknown(exc: Exception) -> "BizException":

        if isinstance(exc, HTTPException):
            message = exc.detail
            status_code=exc.status_code
        else:
            message = _unknown_message
            status_code=_unknown_status_code

        if settings.IS_TEST_ENV:
            message = str(exc)

        return BizException(
            error_code=ErrorCode.unknown_error.name,
            message=message,
            status_code=status_code,
        )

    def to_response(self) -> Response:
        from app.util.api import ApiResult

        content = ApiResult(code=self.error_code, msg=self.message)
        return JSONResponse(
            content=content.model_dump(exclude_none=True),
            status_code=self.status_code,
        )
