import uuid

from sqlmodel import Field, SQLModel


class TableBase(SQLModel):
    id: int = Field(default=None, primary_key=True)
    created_at: str = Field(default=None)
    updated_at: str = Field(default=None)
    deleted: bool = Field(default=False)


class TableUUidBase(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    deleted: bool = Field(default=False)
