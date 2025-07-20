from pydantic_settings import BaseSettings
from fastapi.params import Query

class ApiConfig(BaseSettings):
    PROJECT_NAME: str
    API_V1_STR: str = "/api/v1"

    DEFAULT_PAGE_SIZE: int = 20
    DEFAULT_MAX_PAGE_SIZE: int = 1000
    DEFAULT_MAX_PAGE_NO: int = 100000

    @property
    def page_no_query(self) -> Query:
        return Query(default=1, ge=1, le=self.DEFAULT_MAX_PAGE_NO)

    @property
    def page_size_query(self) -> Query:
        return Query(default=self.DEFAULT_PAGE_SIZE,
              ge=1, le=self.DEFAULT_MAX_PAGE_SIZE)
