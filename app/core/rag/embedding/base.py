from pydantic import BaseModel


class EmbeddingConfig(BaseModel):
    vector_size: int
