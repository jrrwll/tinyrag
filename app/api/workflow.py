from typing import Any

from fastapi import APIRouter, HTTPException

from app.common.deps import SessionDep
from app.entities.workflow import Workflow
from app.schemas.workflow import WorkflowCreate, WorkflowPublic

router = APIRouter(prefix="/workflow", tags=["workflow"])


@router.get("/", response_model=WorkflowPublic)
def get_workflow(session: SessionDep, id: int) -> Any:
    item = session.get(Workflow, id)
    if not item:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return item


@router.post("/", response_model=WorkflowPublic)
def create_workflow(session: SessionDep, workflow_in: WorkflowCreate) -> Any:
    item = Workflow.model_validate(workflow_in)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item
