from typing import Protocol
from pydantic import BaseModel


class MetaConfigProtocol(Protocol):

    @staticmethod
    def get_config_type() -> type[BaseModel]:
        raise NotImplementedError()
