from sqlmodel import Field

from app.core.dataset.enums import DatasetType
from app.entities.base import TableBase


class Dataset(TableBase, table=True):
    type: DatasetType
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1000)
    enable: bool = Field(default=True)
    config: str | None = Field(default=None)
