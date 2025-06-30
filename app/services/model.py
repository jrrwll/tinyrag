
from app.common.deps import SessionDep
from app.entities.model import Model
from app.schemas.model import ModelCreate, ModelPublic
from fastapi import HTTPException

def get_model(session: SessionDep, id: int) -> ModelPublic:
    pass
