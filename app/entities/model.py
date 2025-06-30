from sqlmodel import Field

from app.entities import TableBase
from app.core.model.enums import ModelType, ModelProviderType


class Model(TableBase, table=True):
    type: ModelType = Field(default=ModelType.LLM)
    enable: bool = Field(default=True)
    provider_name: ModelProviderType = Field(max_length=100)
    model_name: str = Field(unique=True, index=True, max_length=100)
    base_url: str = Field(max_length=1000)
    api_key: str | None = Field(default=None, max_length=1000)
    settings: str | None = Field(default=None)
