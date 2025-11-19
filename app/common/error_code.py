from enum import Enum, auto
from typing import Any, Self

from corepy.api.result import ApiResult
from fastapi import Response
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.config import settings


class ErrorCode(Enum):
    unknown_error = auto(), 500, "msg"
    request_error = auto(), "msg"
    request_validation_error = auto(), "msg"
    validation_error = auto(), "missing_fields", "invalid_fields"

    # auth
    email_or_password_incorrect = auto(), 401
    same_new_password = auto()
    login_user_not_active = auto(), 403
    user_not_active = auto()
    user_email_already_exists = auto()
    super_user_cannot_delete = auto()
    invalid_email_domain = auto(), "email_domain"
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
    model_id_not_found = auto(), "id"
    model_type_not_supported = auto(), "model_type"
    model_not_llm = auto(), "model_type"
    model_not_text_embedding = auto(), "model_type"
    model_provider_not_supported = auto(), "model_type", "provider_name"
    model_provider_not_supported_to_edit = auto()
    model_not_set = auto(), "model_type"
    model_name_not_supported = auto(), "model_name"
    model_is_set_in_default = auto()

    vector_store_not_found = auto()
    vector_store_id_not_found = auto(), "id"
    vector_store_is_set_in_default = auto()
    vector_store_not_set = auto()

    storage_not_found = auto()
    storage_id_not_found = auto(), "id"
    storage_not_set = auto()

    workflow_not_found = auto()
    workflow_run_not_found = auto()
    related_workflow_not_found = auto()

    node_not_found = auto()

    code_main_func_undefined = auto()
    code_eval_error = auto(), "msg"

    file_type_not_supported = auto()
    file_not_found = auto()
    file_ids_not_found = auto(), "ids"
    file_not_a_document = auto(), "file_type"
    storage_file_not_found = auto()
    storage_file_not_file = auto()
    storage_file_too_large = auto()

    knowledge_not_found = auto()
    knowledge_id_not_found = auto(), "id"
    knowledge_conversation_not_found = auto()

    def __new__(cls, value: object, *args: Any) -> "ErrorCode":
        obj = object.__new__(cls)
        obj._value_ = value

        if not args:
            obj.status_code = 400
            obj.args = []
            return obj

        status_code = 400
        if args:
            if isinstance(args[0], int):
                status_code = args[0]
                args = args[1:]
        if not args:
            args = []

        obj.status_code = status_code
        obj.args = args
        return obj


class BizException(Exception):

    def __init__(self, status_code: int,
            error_code: str,
            **error_args: str | int | list[str] | list[int]):
        self.status_code = status_code
        self.error_code = error_code
        self.error_args = error_args

    @classmethod
    def create(cls, error_code: ErrorCode,
            **error_args: str | int | list[str] | list[int]) -> Self:
        if set(error_args.keys()) != set(error_code.args):
            raise cls(
                ErrorCode.unknown_error.status_code,
                ErrorCode.unknown_error.name,
                msg=f"error_args must be {error_code.args}"
            )

        return cls(
            status_code=error_code.status_code,
            error_code=error_code.name,
            **error_args,
        )

    @classmethod
    def unknown(cls, exc: Exception) -> Self:
        if isinstance(exc, HTTPException):
            msg = exc.detail
            status_code = exc.status_code
        else:
            msg = 'unknown error'
            status_code = ErrorCode.unknown_error.status_code

        if settings.IS_TEST_ENV:
            msg = str(exc)

        return cls(
            status_code=status_code,
            error_code=ErrorCode.unknown_error.name,
            msg=msg,
        )

    def to_result(self) -> ApiResult[Any]:
        return ApiResult(err_code=self.error_code, err_args=self.error_args)

    def to_response(self) -> Response:
        return JSONResponse(
            content=self.to_result().model_dump(exclude_none=True),
            status_code=self.status_code,
        )
