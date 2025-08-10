from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Callable

from pydantic import BaseModel

from app.common.security import crypt_decrypt, crypt_encrypt
from app.core.meta.enums import FormInputType
from app.core.meta.fields import parse_meta_fields


class MetaProvider[Cfg: BaseModel](ABC):

    def __init__(self, config: dict):
        config_type = self.get_config_type()
        config_dict = decrypt_config_dict(config_type, config)
        self.config = config_type.model_validate(config_dict)

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
        return config

    modified_config = None
    fields = parse_meta_fields(config_type)
    for field in fields:
        field_value = config.get(field.name)
        if not field_value or field.type != FormInputType.Password:
            continue
        if not modified_config:
            modified_config = deepcopy(config)
        modified_config[field.name] = crypt_func(field_value)
    return modified_config or config
