from typing import Any

from app.api import CustomAPIRouter
from app.common.deps import CurrentUser, SessionDep
from app.config import settings
from app.core.task.api import SimpleAsyncTaskPublic
from app.core.task.service import list_knowledge_task
from app.util.api import ApiResult, PageResult

router = CustomAPIRouter(prefix="/task", tags=["task"])


@router.get("/knowledge/list",
            response_model=ApiResult[PageResult[SimpleAsyncTaskPublic]])
def _list_knowledge(
        session: SessionDep,
        current_user: CurrentUser,
        workspace_id: int,
        page_no: int = settings.page_no_query,
        page_size: int = settings.page_size_query,
) -> Any:
    res = list_knowledge_task(session, page_no, page_size, workspace_id, current_user)
    return ApiResult.create(res)


@router.get("/knowledge",
            response_model=ApiResult[PageResult[SimpleAsyncTaskPublic]])
def _get_knowledge(
        session: SessionDep,
        current_user: CurrentUser,
        workspace_id: int,
        page_no: int = settings.page_no_query,
        page_size: int = settings.page_size_query,
) -> Any:
    res = list_knowledge_task(session, page_no, page_size, workspace_id, current_user)
    return ApiResult.create(res)
