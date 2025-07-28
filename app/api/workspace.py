from typing import Any

from app.api import CustomAPIRouter
from app.common.deps import SessionDep
from app.common.error_code import BizException, ErrorCode
from app.config import settings
from app.core.workspace.api import SimpleWorkspacePublic, WorkspaceCreate, \
    WorkspacePublic, WorkspaceUpdate
from app.entities.dao.workspace import page_and_count_workspaces
from app.entities.workspace import Workspace
from app.util.api import ApiResult, IdResult, PageResult

router = CustomAPIRouter(prefix="/workspace", tags=["workspace"])


@router.get("/list", response_model=ApiResult[PageResult[SimpleWorkspacePublic]])
def list(
        session: SessionDep,
        page_no: int = settings.page_no_query,
        page_size: int = settings.page_size_query,
) -> Any:
    entities, count = page_and_count_workspaces(session, page_no, page_size)
    res = PageResult[SimpleWorkspacePublic](
        page_no=page_no,
        page_size=page_size,
        total=count,
        items=[SimpleWorkspacePublic(**entity) for entity in entities],
    )
    return ApiResult.create(res)


@router.get("", response_model=ApiResult[WorkspacePublic])
def get(session: SessionDep, id: int) -> Any:
    entity = session.get(Workspace, id)
    if not entity:
        raise BizException.create(ErrorCode.workspace_not_found, id)

    return ApiResult.create(WorkspacePublic.create(entity))


@router.post("", response_model=ApiResult[IdResult])
def create(session: SessionDep, params: WorkspaceCreate) -> Any:
    entity = params.to_entity()

    session.add(entity)
    session.commit()
    session.refresh(entity)

    return ApiResult.create(IdResult(id=entity.id))


@router.put("", response_model=ApiResult[Any])
def update(session: SessionDep, params: WorkspaceUpdate) -> Any:
    entity = session.get(Workspace, params.id)
    if not entity:
        raise BizException.create(ErrorCode.workspace_not_found, params.id)

    params.update_entity(entity)

    session.add(entity)
    session.commit()

    return ApiResult.create()
