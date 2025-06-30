from pydantic import BaseModel


class OllamaModelSettings(BaseModel):
    base_url: str
    model: str | None = None
    content_length: int = 4096
    max_tokens: int = 4096
    function_calling: bool = False
