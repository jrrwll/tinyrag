from pydantic import BaseModel


class OllamaModelSettings(BaseModel):
    base_url: str
    content_length: int = 4096
    max_tokens: int = 4096
    function_calling: bool = False
