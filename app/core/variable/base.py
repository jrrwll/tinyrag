from typing import Any

from pydantic import BaseModel, Field

from app.core.variable.enums import InputVariableType, FileType


class InputVariable(BaseModel):
    type: InputVariableType = InputVariableType.Text
    name: str = Field(max_length=32)
    display_name: str | None = Field(max_length=32, default=None)
    required: bool = Field(default=True)
    description: str | None = Field(max_length=100, default=None)
    # text, files
    max_length: int | None = Field(default=None)
    # select
    options: list[str] | None = Field(default=None)
    file_types: list[FileType] | None = Field(default=None)
    file_extensions: list[str] | None = Field(default=None)


class AssigningVariable(BaseModel):
    left: str
    right: str
    node_id: int | None = None


class Variable(BaseModel):
    name: str
    value: Any

