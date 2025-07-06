from pydantic import BaseModel, Field, create_model
from typing import Dict, Tuple, Type, Any, Optional


def create_model_type(
        model_name: str,
        fields: Dict[str, Tuple[Type[Any], Dict[str, Any] | Field]],
        base: Type[BaseModel] = BaseModel,
        **kwargs
) -> Type[BaseModel]:
    field_definitions = {}
    for field_name, (field_type, field_config) in fields.items():
        if isinstance(field_config, dict):
            field_config = Field(**field_config)
        field_definitions[field_name] = (field_type, field_config)

    return create_model(
        model_name,
        __base__=base,
        **field_definitions,
        **kwargs
    )

