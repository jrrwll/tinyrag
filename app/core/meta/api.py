from pydantic import BaseModel

from app.core.meta.enums import FormInputType


class MetaBaseField(BaseModel):
    type: FormInputType = FormInputType.Text
    name: str
    required: bool = False

    select: list[str] | None = None


class MetaBaseEntity(BaseModel):
    name: str
    fields: list[MetaBaseField] = []
