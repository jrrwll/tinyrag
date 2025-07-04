from enum import StrEnum

from pydantic import BaseModel


class ExceptionStrategyType(StrEnum):
    DefaultValue = "default_value"
    Node = "node"


class ExceptionDefaultValue(BaseModel):
    name: str
    value: str | int | float | bool | list[str] | list[int] | list[float] | list[bool]
