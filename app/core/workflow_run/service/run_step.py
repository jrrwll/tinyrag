from app.common.deps import SessionDep
from app.core.workflow_run.api import WorkflowRunExecuteStep, \
    WorkflowRunExecuteStepPublic
from app.entities.workflow import Workflow
from app.entities.workflow_run import WorkflowRun


def workflow_run_execute_step(session: SessionDep,
        entity: WorkflowRun, workflow_entity: Workflow,
        params: WorkflowRunExecuteStep) -> WorkflowRunExecuteStepPublic:
    pass
