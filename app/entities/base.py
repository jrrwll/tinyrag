import enum
from datetime import datetime
from typing import Type

from sqlalchemy.orm import declared_attr
from sqlmodel import Column, Enum, Field, SQLModel
from sqlmodel.main import FieldInfo

from app.util.lang import enum_values
from app.util.text import camel_to_snake


class LogTableBase(SQLModel):

    id: int = Field(primary_key=True)
    created_at: datetime

    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:
        return camel_to_snake(cls.__name__)


class TableBase(LogTableBase):

    updated_at: datetime


class BizTableBase(TableBase):

    deleted: bool = False


def enum_field_info[T: enum.Enum](enum_type: Type[T],
        default: T | None = None) -> FieldInfo:
    return Field(sa_column=Column(Enum(enum_type, values_callable=enum_values)),
                 default=default)
