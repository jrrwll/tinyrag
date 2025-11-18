import enum
from datetime import datetime
from typing import Any, Type

from corepy.lang import enum_values
from corepy.text import camel_to_snake
from sqlalchemy.orm import declared_attr
from sqlmodel import Column, Enum, Field, SQLModel


class LogTableBase(SQLModel):

    created_at: datetime

    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:
        return camel_to_snake(cls.__name__)


class TableBase(LogTableBase):
    id: int = Field(primary_key=True)
    updated_at: datetime


class BizTableBase(TableBase):

    deleted: bool = False


def enum_field_info[T: enum.Enum](enum_type: Type[T],
        default: T | None = None) -> Any:
    return Field(sa_column=Column(Enum(enum_type, values_callable=enum_values)),
                 default=default)
