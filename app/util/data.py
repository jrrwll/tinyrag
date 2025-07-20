from dataclasses import dataclass, field
from typing import Any


@dataclass
class OptionalValue[T: Any]:
    value: T | None = field(default=None)

    @property
    def is_present(self) -> bool:
        return self.value is not None

    @property
    def is_empty(self) -> bool:
        return self.value is None

    def __repr__(self) -> str:
        if self.is_present:
            return f"OptionalValue(value={self.value})"
        else:
            return "OptionalValue(empty)"

