# ruff: noqa: E712
from sqlmodel import and_, func, select

from app.common.deps import SessionDep
from app.core.workflow.enums import WorkflowStatus
from app.entities.workflow import Workflow


def page_and_count_workflows(
    session: SessionDep, page_no: int, page_size: int, status: WorkflowStatus | None
) -> tuple[list[dict], int]:  # type: ignore[type-arg]
    conditions = [Workflow.deleted == False]
    if status:
        conditions.append(Workflow.status == status)

    count_statement = (
        select(func.count()).select_from(Workflow).where(and_(*conditions))
    )
    count = session.exec(count_statement).one()

    offset = (page_no - 1) * pa
    ge_size
    limit = page_size

    page_statement = (
        select(  # type: ignore[call-overload]
            Workflow.id,
            Workflow.name,
            Workflow.description,
            Workflow.status,
            Workflow.created_at,
            Workflow.updated_at,
        )
        .select_from(Workflow)
        .where(and_(*conditions))
        .offset(offset)
        .limit(limit)
    )
    models = session.exec(page_statement).mappings().all()
    return [dict(i) for i in models], count
