from sqlmodel import Field

from app.entities import TableBase
from app.entities.enums import ModelType


class Model(TableBase, table=True):
    type: ModelType = Field(default=ModelType.OpenAI)
    enable: bool = Field(default=True)
    name: str = Field(unique=True, index=True, max_length=255)
    description: str = Field(max_length=255)
    config: str = Field()
