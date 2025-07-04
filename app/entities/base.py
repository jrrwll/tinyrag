from datetime import datetime

from sqlmodel import Field, SQLModel


class TableBase(SQLModel):
    id: int = Field(primary_key=True)
    created_at: datetime
    updated_at: datetime
    deleted: bool = Field(default=False)


# class TableUUidBase(SQLModel):
#     id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
#     deleted: bool = Field(default=False)
