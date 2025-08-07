from enum import Enum, auto
from functools import cached_property

from fastapi import HTTPException, Response
from fastapi.responses import JSONResponse

from app.common.i18n import I18nMetaManager
from app.config import settings

_config = I18nMetaManager().error_codes(settings.DEFAULT_LANG)


class ErrorCode(Enum):
    ok = auto(), 200
    unknown_error = auto(), 500
    request_validation_error = auto()
    request_validation_error_detail = auto()

    # auth
    email_or_password_incorrect = auto(), 401
    same_new_password = auto()
    login_user_inactive = auto(), 403
    user_inactive = auto()
    user_email_already_exists = auto()
    super_user_cannot_delete = auto()
    invalid_email_domain = auto()
    login_user_not_found = auto(), 401
    user_not_found = auto()
    user_email_not_found = auto()
    invalid_token = auto(), 401
    invalid_credentials = auto(), 401
    insufficient_permissions = auto(), 403
    permission_already_granted = auto()
    permission_not_granted = auto()

    # feature
    workspace_not_found = auto()
    workspace_name_already_exists = auto()

    model_not_found = auto()
    model_type_not_supported = auto()
    model_provider_not_supported = auto()
    model_provider_not_supported_to_create = auto()
    model_not_set = auto()
    need_specific_type_model = auto()
    model_name_not_supported = auto()
    model_is_set_in_default = auto()

    vector_store_not_found = auto()
    vector_store_is_set_in_default = auto()
    vector_store_not_set = auto()

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

    def __new__(cls, value, status_code: int = 400):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.status_code = status_code
        return obj

    @cached_property
    def message(self):
        message = _config.get(self.name)
        if not message:
            message = self.name.replace("_", " ").capitalize()
        return message


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
        status_code, message = error_code.status_code, error_code.message
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
            message = ErrorCode.unknown_error.message
            status_code=ErrorCode.unknown_error.status_code

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
