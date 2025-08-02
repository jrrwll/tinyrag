from pydantic import BaseModel

from app.core.model.api import ModelPublic


class WorkspaceDetail(BaseModel):
    id: int
    name: str

    llm_model: ModelPublic | None = None
    embedding_model: ModelPublic | None = None
