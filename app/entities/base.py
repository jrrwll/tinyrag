from datetime import datetime

from sqlmodel import Field, SQLModel


class TableBase(SQLModel):
    id: int = Field(primary_key=True)
    created_at: datetime
    updated_at: datetime
    deleted: bool = Field(default=False)


# class TableUUIDBase(SQLModel):
#     id: UUID = Field(default_factory=uuid4, primary_key=True)
#     created_at: datetime
#     deleted: bool = Field(default=False)
