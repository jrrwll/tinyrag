from pydantic import BaseModel, JsonValue

from app.common.error_code import ErrorCode


class ApiResult[T: BaseModel | JsonValue | None](BaseModel):
    code: str = ErrorCode.ok
    msg: str | None = None
    data: T = None

    @classmethod
    def create[R: BaseModel | JsonValue | None](cls, data: R = None) -> "ApiResult[R]":
        return ApiResult(data=data)


# PEP 695 Generic Bounds
class PageResult[T: BaseModel | JsonValue](BaseModel):
    page_no: int
    page_size: int
    total: int
    items: list[T]


class IdResult(BaseModel):
    id: int | str
