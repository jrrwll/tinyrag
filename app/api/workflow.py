from typing import Any

from fastapi import APIRouter, Query

from app.common.api import ApiResult, IdResult, PageResult
from app.common.db import SessionDep
from app.common.error_code import BizException, ErrorCode
from app.config import settings
from app.core.workflow.api import (
    SimpleWorkflowPublic,
    WorkflowCheckListPublic,
    WorkflowCreate,
    WorkflowPublic,
    WorkflowUpdate,
)
from app.core.workflow.check_list import workflow_check_list
from app.core.workflow.enums import WorkflowStatus
from app.entities.dao.workflow import page_and_count_workflows
from app.entities.workflow import Workflow

router = APIRouter(prefix="/workflow", tags=["workflow"])


@router.get("/list", response_model=ApiResult[PageResult[SimpleWorkflowPublic]])
def list(
    session: SessionDep,
    page_no: int = Query(default=1, ge=1, le=100000),
    page_size: int = Query(default=settings.DEFAULT_PAGE_SIZE, ge=1, le=1000),
    status: WorkflowStatus | None = None,
) -> Any:
    entities, count = page_and_count_workflows(session, page_no, page_size, status)
    res = PageResult[SimpleWorkflowPublic](
        page_no=page_no,
        page_size=page_size,
        total=count,
        items=[SimpleWorkflowPublic(**entity) for entity in entities],
    )
    return ApiResult.new(res)


@router.get("", response_model=ApiResult[WorkflowPublic])
def get(session: SessionDep, id: int) -> Any:
    entity = session.get(Workflow, id)
    if not entity:
        raise BizException.new(ErrorCode.workflow_not_found, id)

    return ApiResult.new(WorkflowPublic.new(entity))


@router.post("", response_model=ApiResult[IdResult])
def create(session: SessionDep, params: WorkflowCreate) -> Any:
    entity = params.to_entity()

    session.add(entity)
    session.commit()
    session.refresh(entity)

    return ApiResult.new(IdResult(id=entity.id))


@router.put("", response_model=ApiResult[Any])
def update(session: SessionDep, params: WorkflowUpdate) -> Any:
    entity = session.get(Workflow, params.id)
    if not entity:
        raise BizException.new(ErrorCode.workflow_not_found, params.id)

    params.update_entity(entity)

    session.add(entity)
    session.commit()

    return ApiResult.new()


@router.api_route(
    "/check_list", methods=["GET", "POST"],
    response_model=ApiResult[WorkflowCheckListPublic]
)
def check_list(session: SessionDep, id: int) -> Any:
    entity = session.get(Workflow, id)
    if not entity:
        raise BizException.new(ErrorCode.workflow_not_found, id)

    res = workflow_check_list(session, entity)
    return ApiResult.new(res)
