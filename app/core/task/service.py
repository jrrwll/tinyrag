from sqlmodel import Session

from app.core.task.api import SimpleAsyncTaskPublic
from app.core.task.enums import AsyncTaskType
from app.entities.dao.knowledge import get_knowledges
from app.entities.dao.task import page_and_count_tasks
from app.entities.user import User
from app.util.api import PageResult


def list_knowledge_task(
        session: Session, page_no: int, page_size: int,
        workspace_id: int, current_user: User
) -> PageResult[SimpleAsyncTaskPublic]:
    tenant_id = current_user.tenant_id

    entities, count = page_and_count_tasks(
        session, page_no, page_size,
        AsyncTaskType.knowledge_tasks(), workspace_id, tenant_id)
    ref_ids = [entity.get("ref_id") for entity in entities]

    ref_entities = get_knowledges(session, ref_ids, tenant_id)
    ref_id_names = {str(entity.id): entity.name for entity in ref_entities}
    for entity in entities:
        entity["ref_name"] = ref_id_names.get(entity.get("ref_id"))

    return PageResult[SimpleAsyncTaskPublic](
        page_no=page_no,
        page_size=page_size,
        total=count,
        items=[SimpleAsyncTaskPublic(**entity) for entity in entities],
    )
