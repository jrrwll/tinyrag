from enum import StrEnum
from typing import Any, Type


class VariableType(StrEnum):
    String = "string"
    Integer = "integer"
    Float = "float"
    Boolean = "boolean"

    StringArray = "string_array"
    IntegerArray = "integer_array"
    FloatArray = "float_array"
    BooleanArray = "boolean_array"

    def to_type(self) -> Type[Any]:
        match self:
            case VariableType.String:
                return str
            case VariableType.Integer:
                return int
            case VariableType.Float:
                return float
            case VariableType.Boolean:
                return bool

            case VariableType.StringArray:
                return list[str]
            case VariableType.IntegerArray:
                return list[int]
            case VariableType.FloatArray:
                return list[float]
            case VariableType.BooleanArray:
                return list[bool]
        raise AssertionError(f"Unknown variable type: {self}")


class InputVariableType(StrEnum):
    Text = "text"
    Number = "number"
    Option = "option"
    File = "file"
    Files = "files"


class FileType(StrEnum):
    Picture = "picture"
    Video = "video"
    Audio = "audio"
    Document = "document"
