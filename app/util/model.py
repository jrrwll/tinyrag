from dataclasses import dataclass, field
from typing import Any
from typing import Dict, Tuple, Type

from pydantic import BaseModel, Field, create_model
from pydantic.fields import FieldInfo


def create_model_type( # type: ignore[no-untyped-def]
        model_name: str,
        fields: Dict[str, Tuple[Type[Any], Dict[str, Any] | FieldInfo]],
        base: Type[BaseModel] = BaseModel,
        **kwargs
) -> Type[BaseModel]:
    field_definitions = {}
    for field_name, (field_type, field_config) in fields.items():
        if isinstance(field_config, dict):
            field_config = Field(**field_config)
        field_definitions[field_name] = (field_type, field_config)

    return create_model( # type: ignore[no-any-return]
        model_name,
        __base__=base,
        **field_definitions,
        **kwargs
    )


@dataclass
class OptionalValue[T: Any]:
    value: T | None = field(default=None)

    @property
    def is_present(self):
        return self.value is not None

    @property
    def is_empty(self):
        return self.value is None

    def __repr__(self):
        if self.is_present:
            return f"OptionalValue(value={self.value})"
        else:
            return "OptionalValue(empty)"
