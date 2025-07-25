import enum
from datetime import datetime
from typing import Type

from sqlmodel import Column, Enum, Field, SQLModel
from sqlmodel.main import FieldInfo

from app.util.lang import enum_values


class TableBase(SQLModel):
    id: str = Field(primary_key=True)
    created_at: datetime
    updated_at: datetime
    deleted: bool = False


def enum_field_info[T: enum.Enum](enum_type: Type[T],
        default: T | None = None) -> FieldInfo:
    return Field(sa_column=Column(Enum(enum_type, values_callable=enum_values)),
                 default=default)
