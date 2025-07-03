import json
from typing import Annotated, Any

from pydantic import BaseModel

from app.core.model.base import LLMPrompt, ModelParams, StructuredOutput
from app.core.workflow.enums import NodeType, WorkflowType, WorkflowVersionType
from app.core.workflow.exception_strategy import (
    ExceptionDefaultValue,
    ExceptionStrategyType,
)
from app.core.workflow.node.classify import ClassifyTopic, ClassifyVariable
from app.core.workflow.node.http import HttpConfig
from app.core.workflow.variable import InputVariable, Variable
from app.entities.workflow import Workflow


class WorkflowCreate(BaseModel):
    type: WorkflowType
    name: str
    description: str | None = None

    # graph
    graph: "WorkflowGraph"

    def to_entity(self) -> Workflow:
        update_dict = {}
        if self.graph:
            update_dict["graph"] = json.dumps(self.graph)
        return Workflow.model_validate(self, update=update_dict)


class WorkflowUpdate(WorkflowCreate):
    id: int

    def update_entity(self, entity: Workflow) -> None:
        update_dict = self.model_dump(exclude_none=True)
        update_dict.update(
            {
                "graph": json.dumps(self.graph),
            }
        )
        entity.sqlmodel_update(update_dict)


class WorkflowPublic(WorkflowCreate):
    id: int
    created_at: str
    updated_at: str
    version: WorkflowVersionType

    @staticmethod
    def new(item: Workflow) -> "WorkflowPublic":
        item_dict = item.model_dump(exclude_none=True)
        if item.graph:
            item_dict["graph"] = json.loads(item.graph)
        return WorkflowPublic(**item_dict)


class WorkflowGraph(BaseModel):
    nodes: list["Node"]
    edges: list["Edge"]

    front_info: str | None = None


class Node(BaseModel):
    id: int
    name: str
    description: str | None = None
    type: NodeType

    settings: "NodeSettings"
    front_info: str | None = None

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Node):
            return False
        else:
            return self.id == other.id


class Edge(BaseModel):
    source: int
    target: int

    front_info: str | None = None

    def __hash__(self) -> int:
        return hash((self.source, self.target))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Edge):
            return False
        else:
            return self.source == other.source and self.target == other.target


class NodeSettings(BaseModel):
    output_variable: str | None = None

    input_variables: Annotated[list[InputVariable] | None, "start"] = None
    end_variables: list[Variable] | None = None

    model_id: int | None = None
    model_params: ModelParams | None = None
    prompts: list[LLMPrompt] | None = None
    structured_output: list[StructuredOutput] | None = None

    exception_strategy: ExceptionStrategyType | None = None
    exception_node_id: int | None = None
    exception_default_values: list[ExceptionDefaultValue] | None = None

    conditions: str | None = None
    true_node_id: int | None = None
    false_node_id: int | None = None

    classify_variable: ClassifyVariable | None = None
    classify_prompt: str | None = None
    classify_topics: list[ClassifyTopic] | None = None

    code: str | None = None
    code_args: list[str] | None = None

    template: str | None = None
    # template_type: TemplateType | None = None
    template_args: list[Variable] | None = None

    extract_file: str | None = None

    http_config: HttpConfig | None = None
