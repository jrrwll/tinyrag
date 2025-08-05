from pydantic import BaseModel
from typing import get_origin, get_args, Union, Annotated

from app.common.app_dispatch import request_id_var
from app.common.i18n import I18nBaseEntity, I18nMetaManager
from app.core.meta.api import MetaBaseEntity, MetaBaseField
from app.core.meta.enums import FormInputType
from app.core.model.enums import ModelType
from app.core.model.provider import ModelProviderFactory
from app.core.vector_store.enums import VectorStoreType
from app.core.vector_store.provider.base import VectorProvideFactory
from app.util.lang import strip_type


# todo redis cache
def list_model_providers(model_type: ModelType) -> list[MetaBaseEntity]:
    msgs = I18nMetaManager().model_providers(
        request_id_var.get()).get(model_type, {})

    providers = ModelProviderFactory.get_implements(model_type)
    items = []
    for provider_name, cls in providers.items():
        msg = msgs.get(provider_name, I18nBaseEntity())

        config_type: type[BaseModel] = cls.get_config_type()
        fields = _parse_fields(config_type)
        if msg.fields:
            for field in fields:
                field_msg = msg.fields.get(field.name)
                if not field_msg:
                    continue

                field.display_name = field_msg.display_name
                field.description = field_msg.description

        items.append(MetaBaseEntity(
            name=provider_name,
            display_name=msg.display_name,
            description=msg.description,
            icon=msg.icon,
            fields=fields,
        ))

    return items


def list_vector_store_providers() -> list[MetaBaseEntity]:
    msgs = I18nMetaManager().vector_store_providers(
        request_id_var.get())

    items = []
    for vector_store_type in VectorStoreType:
        msg = msgs.get(vector_store_type.value, I18nBaseEntity())

        config_type = (VectorProvideFactory.get_vector_class(vector_store_type)
                       .get_config_type())
        fields = _parse_fields(config_type)
        items.append(MetaBaseEntity(
            name=vector_store_type.value,
            display_name=msg.display_name,
            description=msg.description,
            icon=msg.icon,
            fields=fields,
        ))
    return items


def _parse_fields(config_type: type[BaseModel]) -> list[MetaBaseField]:
    fields = []
    for name, field_info in config_type.model_fields.items():
        field = MetaBaseField(
            name=name,
            required=field_info.default is not None,
        )
        fields.append(field)

        json_schema_extra = field_info.json_schema_extra or {}
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
            else:
                typ = FormInputType.Text
        field.type = typ

    return fields
