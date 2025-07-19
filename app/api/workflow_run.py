from typing import Any

from fastapi import APIRouter

from app.common.api import ApiResult, IdResult
from app.common.db import SessionDep
from app.common.error_code import BizException, ErrorCode
from app.core.workflow_run.api import (WorkflowRunCreate, WorkflowRunExecute,
                                       WorkflowRunExecutePublic,
                                       WorkflowRunExecuteStep,
                                       WorkflowRunExecuteStepPublic,
                                       WorkflowRunPublic)
from app.core.workflow_run.service.run_step import workflow_run_execute, \
    workflow_run_execute_step
from app.entities.workflow import Workflow
from app.entities.workflow_run import WorkflowRun

router = APIRouter(prefix="/workflow/run", tags=["workflow", "workflow_run"])


@router.get("", response_model=ApiResult[WorkflowRunPublic])
def get(session: SessionDep, id: int) -> Any:
    entity = session.get(WorkflowRun, id)
    if not entity:
        raise BizException.new(ErrorCode.workflow_run_not_found, id)

    workflow_entity = session.get(Workflow, entity.workflow_id)
    if not workflow_entity:
        raise BizException.new(ErrorCode.related_workflow_not_found, entity.workflow_id)

    return ApiResult.new(WorkflowRunPublic.new(entity, workflow_entity))


@router.post("", response_model=ApiResult[IdResult])
def create(session: SessionDep, params: WorkflowRunCreate) -> Any:
    workflow_entity = session.get(Workflow, params.workflow_id)
    if not workflow_entity:
        raise BizException.new(ErrorCode.workflow_not_found, params.workflow_id)

    entity = params.to_entity()

    session.add(entity)
    session.commit()
    session.refresh(entity)

    return ApiResult.new(IdResult(id=entity.id))


@router.post("/execute", response_model=ApiResult[WorkflowRunExecutePublic])
def execute(session: SessionDep, params: WorkflowRunExecute) -> Any:
    entity = session.get(WorkflowRun, params.id)
    if not entity:
        raise BizException.new(ErrorCode.workflow_run_not_found, params.id)

    workflow_entity = session.get(Workflow, entity.workflow_id)
    if not workflow_entity:
        raise BizException.new(ErrorCode.related_workflow_not_found, entity.workflow_id)

    res = workflow_run_execute(session, entity, workflow_entity, params)
    return ApiResult.new(res)


@router.post("/execute_step", response_model=ApiResult[WorkflowRunExecuteStepPublic])
def execute_step(session: SessionDep, params: WorkflowRunExecuteStep) -> Any:
    entity = session.get(WorkflowRun, params.id)
    if not entity:
        raise BizException.new(ErrorCode.workflow_run_not_found, params.id)

    workflow_entity = session.get(Workflow, entity.workflow_id)
    if not workflow_entity:
        raise BizException.new(ErrorCode.related_workflow_not_found, entity.workflow_id)

    res = workflow_run_execute_step(session, entity, workflow_entity, params)
    return ApiResult.new(res)
