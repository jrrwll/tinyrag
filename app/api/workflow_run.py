from typing import Any

from fastapi import APIRouter

from app.common.deps import SessionDep
from app.common.error_code import BizException, ErrorCode
from app.core.workflow_run.api import (
    WorkflowRunCreate,
    WorkflowRunPublic,
    WorkflowRunStepCreate,
)
from app.entities.workflow_run import WorkflowRun

router = APIRouter(prefix="/workflow/run", tags=["workflow", "workflow_run"])


@router.get("", response_model=WorkflowRunPublic)
def get(session: SessionDep, id: int) -> Any:
    entity = session.get(WorkflowRun, id)
    if not entity:
        raise BizException.new(ErrorCode.workflow_run_not_found, id)

    pass


@router.post("")
def run(session: SessionDep, params: WorkflowRunCreate) -> Any:
    pass
    return {"id": id}


@router.post("/run_step")
def run_step(session: SessionDep, params: WorkflowRunStepCreate) -> Any:
    pass
    return {"id": id}


@router.delete("")
def delete(session: SessionDep, id: int) -> Any:
    entity = session.get(WorkflowRun, id)
    if not entity:
        raise BizException.new(ErrorCode.workflow_run_not_found, id)

    session.delete(entity)
    session.commit()
    return {"id": id}
