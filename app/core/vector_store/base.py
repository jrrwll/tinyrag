from pydantic import BaseModel


class VectorStoreConfig(BaseModel):
    vector_store_id: int
