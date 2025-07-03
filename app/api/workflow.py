from typing import Any

from fastapi import APIRouter

from app.common.deps import SessionDep
from app.common.error_code import BizException, ErrorCode
from app.core.workflow.api import (
    WorkflowCheckListPublic,
    WorkflowCreate,
    WorkflowPublic,
    WorkflowUpdate,
)
from app.entities.workflow import Workflow

router = APIRouter(prefix="/workflow", tags=["workflow"])


@router.get("", response_model=WorkflowPublic)
def get(session: SessionDep, id: int) -> Any:
    entity = session.get(Workflow, id)
    if not entity:
        raise BizException.new(ErrorCode.workflow_not_found, id)

    return WorkflowPublic.new(entity)


@router.post("", response_model=WorkflowPublic)
def create(session: SessionDep, params: WorkflowCreate) -> Any:
    entity = params.to_entity()

    session.add(entity)
    session.commit()
    session.refresh(entity)

    return WorkflowPublic.new(entity)


@router.put("", response_model=WorkflowPublic)
def update(session: SessionDep, params: WorkflowUpdate) -> Any:
    entity = session.get(Workflow, params.id)
    if not entity:
        raise BizException.new(ErrorCode.workflow_not_found, params.id)

    params.update_entity(entity)

    session.add(entity)
    session.commit()
    session.refresh(entity)

    return WorkflowPublic.new(entity)


@router.api_route("/check_list", methods=["GET", "POST"],
                  response_model=WorkflowCheckListPublic)
def check_list(session: SessionDep, id: int) -> Any:
    entity = session.get(Workflow, id)
    if not entity:
        raise BizException.new(ErrorCode.workflow_not_found, id)

