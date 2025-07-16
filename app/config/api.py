from pydantic_settings import BaseSettings


class ApiConfig(BaseSettings):
    PROJECT_NAME: str
    API_V1_STR: str = "/api/v1"

    DEFAULT_PAGE_SIZE: int = 20
    DEFAULT_MAX_PAGE_SIZE: int = 1000
    DEFAULT_MAX_PAGE_NO: int = 100000
