from pydantic_settings import BaseSettings
from pydantic import PositiveInt


class StorageSettings(BaseSettings):
    STORAGE_LIST_FILE_MAX_COUNT: PositiveInt = 1000
    STORAGE_FILE_MAX_SIZE: PositiveInt = 20 # MB
