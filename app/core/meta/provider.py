from abc import ABC, abstractmethod
from typing import Callable

from pydantic import BaseModel, SecretStr

from app.common.security import crypt_decrypt, crypt_encrypt
from app.core.meta.enums import FormInputType
from app.core.meta.fields import parse_meta_fields


class MetaProvider[Cfg: BaseModel](ABC):

    def __init__(self, config: dict):
        config_type = self.get_config_type()
        decrypt_config_dict(config_type, config)
        self.config = config_type.model_validate(config)

    @staticmethod
    @abstractmethod
    def get_config_type() -> type[Cfg]:
        raise NotImplementedError


# form to db
def encrypt_config_dict(config_type: type[BaseModel], config: dict):
    _crypt_config_dict(config_type, config, crypt_encrypt)


# db to using
def decrypt_config_dict(config_type: type[BaseModel], config: dict):
    _crypt_config_dict(config_type, config, crypt_decrypt)


def _crypt_config_dict(config_type: type[BaseModel], config: dict,
        crypt_func: Callable[[str], str]):
    if not config:
        return

    fields = parse_meta_fields(config_type)
    for field in fields:
        field_value = config.get(field.name)
        if not field_value or field.type != FormInputType.Password:
            continue
        # encrypt case
        if isinstance(field_value, SecretStr):
            field_value = field_value.get_secret_value()
        config[field.name] = crypt_func(field_value)
