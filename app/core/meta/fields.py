from functools import cache

from pydantic import BaseModel, SecretStr

from app.core.meta.api import MetaBaseField
from app.core.meta.enums import FormInputType
from app.util.lang import strip_type


@cache
def parse_meta_fields(config_type: type[BaseModel]) -> list[MetaBaseField]:
    fields = []
    if config_type.model_json_schema().get("builtin"):
        return fields

    for name, field_info in config_type.model_fields.items():
        json_schema_extra = field_info.json_schema_extra or {}
        if json_schema_extra.get("builtin"):
            continue

        field = MetaBaseField(
            name=name,
            required=field_info.is_required(),
        )
        fields.append(field)

        typ = json_schema_extra.get("type")
        if typ:
            if typ == FormInputType.Select:
                field.select = json_schema_extra.get("select")
        else:
            annotation = field_info.annotation
            annotation_type = strip_type(annotation)
            if annotation_type == int or annotation_type == float:
                typ = FormInputType.Number
            elif annotation_type == bool:
                typ = FormInputType.Switch
            elif annotation_type == SecretStr:
                typ = FormInputType.Password
            else:
                typ = FormInputType.Text
        field.type = typ

    return fields
