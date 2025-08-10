from typing import Self

from pydantic import BaseModel, ValidationError

from app.core.meta.api import MetaBaseEntity
from app.core.meta.base import MetaConfigProtocol
from app.core.meta.enums import FormInputType
from app.core.meta.fields import parse_meta_fields
from app.core.model.enums import BUILTIN_MODEL_PROVIDER_NAME, ModelType
from app.core.model.provider import ModelProviderFactory
from app.core.storage.enums import StorageType
from app.core.storage.provider.base import StorageProviderFactory
from app.core.vector_store.enums import VectorStoreType
from app.core.vector_store.provider.base import VectorProviderFactory


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
            fields = parse_meta_fields(config_type)

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
        fields = parse_meta_fields(config_type)
        for field in fields:
            if field.type == FormInputType.Password:
                config[field.name] = "**********"
