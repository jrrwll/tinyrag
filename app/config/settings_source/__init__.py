from enum import StrEnum

from pydantic_settings import BaseSettings


class SettingsSourceName(StrEnum):
    File = "file"
    NACOS = "nacos"
    APOLLO = "apollo"


class SettingsSourceConfig(BaseSettings):
    SOURCE_NAME: SettingsSourceName = SettingsSourceName.File
