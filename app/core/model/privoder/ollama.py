from pydantic import BaseModel


# settings = OllamaModelSettings.model_validate_json(model.settings)
class OllamaModelSettings(BaseModel):
    content_length: int = 4096
    max_tokens: int = 4096
    function_calling: bool = False
