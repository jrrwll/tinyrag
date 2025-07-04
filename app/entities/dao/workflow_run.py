from sqlmodel import select

from app.common.deps import SessionDep
from app.entities.workflow_run import WorkflowRun


def get_workflow_run(
    session: SessionDep, workflow_id: int
) -> list[WorkflowRun]:
    statement = select(WorkflowRun).select_from(WorkflowRun)
    statement.filter(WorkflowRun.workflow_id == workflow_id)

    return session.exec(statement).all()
