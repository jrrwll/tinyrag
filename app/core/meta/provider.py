from typing import Callable, Self

from pydantic import BaseModel, ValidationError

from app.common.security import crypt_decrypt, crypt_encrypt
from app.core.meta.api import MetaBaseEntity, MetaBaseField
from app.core.meta.base import MetaConfigProtocol
from app.core.meta.enums import FormInputType
from app.core.model.enums import BUILTIN_MODEL_PROVIDER_NAME, ModelType
from app.core.model.provider import ModelProviderFactory
from app.core.storage.enums import StorageType
from app.core.storage.provider.base import StorageProviderFactory
from app.core.vector_store.enums import VectorStoreType
from app.core.vector_store.provider.base import VectorProviderFactory
from app.util.lang import strip_type


# todo redis cache
class ProviderMetaService:

    @classmethod
    def from_model(cls, model_type: ModelType) -> Self:
        providers = ModelProviderFactory.get_implements(model_type)
        return cls(providers)

    @classmethod
    def from_vector_store(cls) -> Self:
        providers = {}
        for typ in VectorStoreType:
            provider_class = VectorProviderFactory.get_provider_class(typ)
            providers[typ] = provider_class
        return cls(providers)

    @classmethod
    def from_storage(cls) -> Self:
        providers = {}
        for typ in StorageType:
            provider_class = StorageProviderFactory.get_provider_class(typ)
            providers[typ] = provider_class
        return cls(providers)

    def __init__(self, providers: dict[str, type[MetaConfigProtocol]]):
        self.providers = providers

    def list(self) -> list[MetaBaseEntity]:
        items = []
        for provider_name, cls in self.providers.items():
            config_type: type[BaseModel] = cls.get_config_type()
            fields = _parse_fields(config_type)

            items.append(MetaBaseEntity(
                name=provider_name,
                fields=fields,
            ))

        return items

    # validate form
    def validate_config_dict(self, provider_name: str, config: dict):
        if provider_name == BUILTIN_MODEL_PROVIDER_NAME:
            return

        cls = self.providers.get(provider_name)
        if not cls:
            raise ValidationError(f"provider {provider_name} is unsupported")

        config_type = cls.get_config_type()
        config_type.model_validate(config)

    # for display
    def desensitizing_config_dict(self, provider_name: str, config: dict):
        cls = self.providers.get(provider_name)
        if not cls:
            return

        config_type = cls.get_config_type()
        fields = _parse_fields(config_type)
        for field in fields:
            if field.type == FormInputType.Password:
                config[field.name] = "**********"

    # form to db
    def encrypt_config_dict(self, provider_name: str, config: dict):
        self._crypt_config_dict(provider_name, config, crypt_encrypt)

    # db to using
    def decrypt_config_dict(self, provider_name: str, config: dict):
        self._crypt_config_dict(provider_name, config, crypt_decrypt)

    def _crypt_config_dict(self, provider_name: str, config: dict,
            crypt_func: Callable[[str], str]):
        cls = self.providers.get(provider_name)
        if not cls:
            return

        config_type = cls.get_config_type()
        fields = _parse_fields(config_type)
        for field in fields:
            field_value = config.get(field.name)
            if not field_value or field.type != FormInputType.Password:
                continue
            config[field.name] = crypt_func(field_value)


def _parse_fields(config_type: type[BaseModel]) -> list[MetaBaseField]:
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
            else:
                typ = FormInputType.Text
        field.type = typ

    return fields
