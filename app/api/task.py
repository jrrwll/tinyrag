from typing import Any

from fastapi import APIRouter, HTTPException

from app.core.deps import SessionDep
from app.models.task import Task
from app.schemas.task import TaskPublic

router = APIRouter(prefix="/task", tags=["task"])


@router.get("/", response_model=TaskPublic)
def get_workflow(session: SessionDep, id: int) -> Any:
    item = session.get(Task, id)
    if not item:
        raise HTTPException(status_code=404, detail="Task not found")
    return item
