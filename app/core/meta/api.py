from pydantic import BaseModel

from app.core.meta.enums import FormInputType


class MetaBaseField(BaseModel):
    type: FormInputType = FormInputType.Text
    name: str
    required: bool = False
    display_name: str | None = None
    description: str | None = None

    select: list[str] | None = None


class MetaBaseEntity(BaseModel):
    name: str
    display_name: str | None = None
    description: str | None = None
    icon: str | None = None

    fields: list[MetaBaseField] = []
