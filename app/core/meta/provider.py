from abc import ABC, abstractmethod
from typing import Callable

from pydantic import BaseModel, SecretStr
from copy import deepcopy
from app.common.security import crypt_decrypt, crypt_encrypt
from app.core.meta.enums import FormInputType
from app.core.meta.fields import parse_meta_fields


class MetaProvider[Cfg: BaseModel](ABC):

    def __init__(self, config: dict):
        config_type = self.get_config_type()
        decrypt_config = decrypt_config_dict(config_type, config)
        self.config = config_type.model_validate(decrypt_config)

    @staticmethod
    @abstractmethod
    def get_config_type() -> type[Cfg]:
        raise NotImplementedError


# form to db
def encrypt_config_dict(config_type: type[BaseModel], config: dict) -> dict:
    return _crypt_config_dict(config_type, config, crypt_encrypt)


# db to using
def decrypt_config_dict(config_type: type[BaseModel], config: dict) -> dict:
    return _crypt_config_dict(config_type, config, crypt_decrypt)


def _crypt_config_dict(config_type: type[BaseModel], config: dict,
        crypt_func: Callable[[str], str]) -> dict:
    if not config:
        config

    modified_config = None
    fields = parse_meta_fields(config_type)
    for field in fields:
        field_value = config.get(field.name)
        if not field_value or field.type != FormInputType.Password:
            continue
        # encrypt case
        if isinstance(field_value, SecretStr):
            field_value = field_value.get_secret_value()
        if not modified_config:
            modified_config = deepcopy(config)
        modified_config[field.name] = crypt_func(field_value)
    return modified_config or config
