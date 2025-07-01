from typing import Any

from fastapi import APIRouter, HTTPException

from app.common.deps import SessionDep
from app.entities.workflow_run import WorkflowRun
from app.schemas.workflow_run import WorkflowInput, WorkflowOutput, WorkflowRunPublic

router = APIRouter(prefix="/workflow/run", tags=["workflow", "workflow_run"])


@router.get("/", response_model=WorkflowRunPublic)
def get_workflow_run(session: SessionDep, id: int) -> Any:
    item = session.get(WorkflowRun, id)
    if not item:
        raise HTTPException(status_code=404, detail="Task not found")
    return item


@router.post("/", response_model=WorkflowOutput)
def run_workflow(session: SessionDep, workflow_run_in: WorkflowInput) -> Any:
    pass
