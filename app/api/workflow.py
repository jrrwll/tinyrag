from typing import Annotated, Any

from app.api import CustomAPIRouter
from app.common.deps import SessionDep
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
from corepy.api.result import ApiResult, IdResult, PageResult

router = CustomAPIRouter(prefix="/workflow", tags=["workflow"])


@router.get("/list", response_model=ApiResult[PageResult[SimpleWorkflowPublic]])
def list(
    session: SessionDep,
    page_no: int = settings.page_no_query,
    page_size: int = settings.page_size_query,
    status: WorkflowStatus | None = None,
) -> Any:
    entities, count = page_and_count_workflows(session, page_no, page_size, status)
    res = PageResult[SimpleWorkflowPublic](
        page_no=page_no,
        page_size=page_size,
        total=count,
        items=[SimpleWorkflowPublic(**entity) for entity in entities],
    )
    return ApiResult.ok(res)


@router.get("", response_model=ApiResult[WorkflowPublic])
def get(session: SessionDep, id: int) -> Any:
    entity = session.get(Workflow, id)
    if not entity:
        raise BizException.create(ErrorCode.workflow_not_found)

    return ApiResult.ok(WorkflowPublic.new(entity))


@router.post("", response_model=ApiResult[IdResult])
def create(session: SessionDep, params: WorkflowCreate) -> Any:
    entity = params.to_entity()

    session.add(entity)
    session.commit()
    session.refresh(entity)

    return ApiResult.ok(IdResult(id=entity.id))


@router.put("", response_model=ApiResult[Any])
def update(session: SessionDep, params: WorkflowUpdate) -> Any:
    entity = session.get(Workflow, params.id)
    if not entity:
        raise BizException.create(ErrorCode.workflow_not_found)

    params.update_entity(entity)

    session.add(entity)
    session.commit()

    return ApiResult.ok()


@router.api_route(
    "/check-list", methods=["GET", "POST"],
    response_model=ApiResult[WorkflowCheckListPublic]
)
def check_list(session: SessionDep, id: int) -> Any:
    entity = session.get(Workflow, id)
    if not entity:
        raise BizException.create(ErrorCode.workflow_not_found)

    res = workflow_check_list(session, entity)
    return ApiResult.ok(res)
