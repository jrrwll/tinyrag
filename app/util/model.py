import json
from typing import Any, Dict, Tuple, Type

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


def dump_json(a: Any):
    if isinstance(a, BaseModel):
        return json.dumps(a.model_dump(), ensure_ascii=False)
    else:
        return json.dumps(a, ensure_ascii=False)


# {"a": "{}", "b": "[]"} -> {"a": BaseModel, "b": []}
def load_and_update_dict(d: dict[str, Any],
        *keys: str, **model_classes: type[BaseModel]) -> None:
    new_dict = {}
    for key in keys:
        if key in d:
            new_dict[key] = json.loads(d[key])

    for key, model_cls in model_classes.items():
        if key in d:
            new_dict[key] = model_cls.model_validate_json(d[key])

    d.update(new_dict)


# {"a": [1]} -> {"a": "[1]"}
def dump_and_update_dict(d: dict[str, Any], *keys: str) -> None:
    new_dict = {}
    for key in keys:
        if key in d:
            new_dict[key] = dump_json(d[key])
    d.update(new_dict)


def model_validate_dict[T: BaseModel](
        raw_dict: dict[str, dict[str, dict]], model: type[T]
) -> dict[str, dict[str, T]]:
    new_dict = {}
    for k1, d in raw_dict.items():
        new_d = {}
        for k2, v in d.items():
            new_d[k2] = model.model_validate(v)
        new_dict[k1] = new_d

    return new_dict


def get_extra_schema(model_cls: type[BaseModel]) -> dict[str, dict[str, Any]]:
    fields = {}
    for field_name, field_info in model_cls.model_fields.items():
        json_schema_extra = field_info.json_schema_extra
        if json_schema_extra and isinstance(json_schema_extra, dict):
            fields[field_name] = json_schema_extra

    return fields
