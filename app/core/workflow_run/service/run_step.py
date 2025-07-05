from app.common.deps import SessionDep
from app.core.workflow_run.api import WorkflowRunExecute, \
    WorkflowRunExecuteStep, \
    WorkflowRunExecuteStepPublic, \
    WorkflowRunExecutePublic
from app.core.workflow_run.service.graph import GraphRunner
from app.entities.workflow import Workflow
from app.entities.workflow_run import WorkflowRun


def workflow_run_execute(session: SessionDep,
        entity: WorkflowRun, workflow_entity: Workflow,
        params: WorkflowRunExecute) -> WorkflowRunExecutePublic:
    runner = GraphRunner()

    runner.run()

    output_variables = runner.output_variables
    return WorkflowRunExecutePublic(output_variables=output_variables)


def workflow_run_execute_step(session: SessionDep,
        entity: WorkflowRun, workflow_entity: Workflow,
        params: WorkflowRunExecuteStep) -> WorkflowRunExecuteStepPublic:
    node_id = params.node_id

    runner = GraphRunner()

    runner.run_node(node_id)

    output_variables = runner.output_variables
    return WorkflowRunExecuteStepPublic(output_variables=output_variables)
