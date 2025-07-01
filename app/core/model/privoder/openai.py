from pydantic import BaseModel


class OpenaiModelSettings(BaseModel):
    group_id: str | None = None
