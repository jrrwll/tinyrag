from typing import Any

from pydantic import BaseModel


def get_extra_schema(model_cls: type[BaseModel]) -> dict[str, dict[str, Any]]:
    fields = {}
    for field_name, field_info in model_cls.model_fields.items():
        json_schema_extra = field_info.json_schema_extra
        if json_schema_extra and isinstance(json_schema_extra, dict):
            fields[field_name] = json_schema_extra

    return fields
