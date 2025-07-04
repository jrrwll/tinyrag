from enum import StrEnum


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
