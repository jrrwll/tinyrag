from pydantic import BaseModel


class OpenaiModelSettings(BaseModel):
    base_url: str | None = None
    api_key: str | None = None
    group_id: str | None = None
