from enum import StrEnum

from pydantic import BaseModel, Field

from app.core.workflow.file import FileType


class VariableType(StrEnum):
    String = "string"
    Integer = "integer"
    Float = "float"
    Boolean = "boolean"

    StringArray = "string_array"
    IntegerArray = "integer_array"
    FloatArray = "float_array"
    BooleanArray = "boolean_array"


class InputVariableType(StrEnum):
    Text = "text"
    Number = "number"
    Option = "option"
    File = "file"
    Files = "files"


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


class Variable(BaseModel):
    name: str
    value: str
    node_id: int | None = None
