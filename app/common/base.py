from pydantic import BaseModel


# PEP 695 Generic Bounds
class PageResult[T: BaseModel](BaseModel):
    page_no: int
    page_size: int
    total: int
    items: list[T]
