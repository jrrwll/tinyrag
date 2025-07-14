from pydantic import BaseModel


class ApiResult[T: BaseModel](BaseModel):
    code: int = 0
    msg: str | None = None
    data: T | None = None


# PEP 695 Generic Bounds
class PageResult[T: BaseModel](BaseModel):
    page_no: int
    page_size: int
    total: int
    items: list[T]


def wrap_api_result[T: BaseModel | None](data: T = None) -> ApiResult[T]:
    return ApiResult(data=data)
