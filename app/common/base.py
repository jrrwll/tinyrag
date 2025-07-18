from pydantic import BaseModel


class ApiResult[T: BaseModel](BaseModel):
    code: int = 0
    msg: str | None = None
    data: T | None = None

    @classmethod
    def new[R: BaseModel | None](cls, data: R = None) -> ApiResult[R]:
        return ApiResult(data=data)


# PEP 695 Generic Bounds
class PageResult[T: BaseModel](BaseModel):
    page_no: int
    page_size: int
    total: int
    items: list[T]


class IdResult(BaseModel):
    id: int | str


def wrap_api_result[T: BaseModel | None](data: T = None) -> ApiResult[T]:
    return ApiResult(data=data)
