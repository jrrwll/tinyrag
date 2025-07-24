from enum import Enum
from typing import Type, Any


def enum_values[T: Enum](enum_type: Type[T]) -> list[Any]:
    return [m.value for m in enum_type]
