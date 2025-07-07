from typing import Any

from pydantic import BaseModel, Field

from app.core.model.base import LLMPrompt, ModelParams, StructuredOutput
from app.core.node.runner.classify import ClassifyTopic, ClassifyVariable
from app.core.node.runner.http import HttpConfig
from app.core.variable.base import ContextVariable, InputVariable
from app.core.workflow.enums import NodeType
from app.core.workflow.exception_strategy import (
    ExceptionDefaultValue,
    ExceptionStrategyType,
)


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
    output_variable: str | None = Field(default=None)

    start_variables: list[InputVariable] | None = Field(
        default=None, json_schema_extra={"allow_types": [NodeType.Start]}
    )

    context_variables: list[ContextVariable] | None = Field(
        default=None, json_schema_extra={"disallow_types": [NodeType.Start]}
    )

    end_variables: list[ContextVariable] | None = Field(
        default=None, json_schema_extra={"allow_types": [NodeType.End]}
    )

    model_id: int | None = Field(
        default=None,
        json_schema_extra={"allow_types": [NodeType.LLM, NodeType.Classify]},
    )
    model_params: ModelParams | None = Field(
        default=None,
        json_schema_extra={"allow_types": [NodeType.LLM, NodeType.Classify]},
    )
    user_prompt: str | None = Field(
        default=None,
        json_schema_extra={"allow_types": [NodeType.LLM]},
    )
    advanced_prompts: list[LLMPrompt] | None = Field(
        default=None, json_schema_extra={"allow_types": [NodeType.LLM], "required": False}
    )
    structured_output: list[StructuredOutput] | None = Field(
        default=None, json_schema_extra={"allow_types": [NodeType.LLM]}
    )

    exception_strategy: ExceptionStrategyType | None = None
    exception_node_id: int | None = None
    exception_default_values: list[ExceptionDefaultValue] | None = None

    conditions: str | None = Field(
        default=None, json_schema_extra={"allow_types": [NodeType.Condition]}
    )
    true_node_id: int | None = Field(
        default=None, json_schema_extra={"allow_types": [NodeType.Condition]}
    )
    false_node_id: int | None = Field(
        default=None, json_schema_extra={"allow_types": [NodeType.Condition]}
    )

    classify_variable: ClassifyVariable | None = Field(
        default=None, json_schema_extra={"allow_types": [NodeType.Classify]}
    )
    classify_prompt: str | None = Field(
        default=None, json_schema_extra={"allow_types": [NodeType.Classify]}
    )
    classify_topics: list[ClassifyTopic] | None = Field(
        default=None, json_schema_extra={"allow_types": [NodeType.Classify]}
    )

    code: str | None = Field(
        default=None, json_schema_extra={"allow_types": [NodeType.Code]}
    )
    code_args: list[str] | None = Field(
        default=None, json_schema_extra={"allow_types": [NodeType.Code]}
    )

    template: str | None = Field(
        default=None, json_schema_extra={"allow_types": [NodeType.Template]}
    )
    # template_type: TemplateType | None = None
    template_args: list[ContextVariable] | None = Field(
        default=None, json_schema_extra={"allow_types": [NodeType.Template]}
    )

    extract_file: str | None = Field(
        default=None, json_schema_extra={"allow_types": [NodeType.DocExtract]}
    )

    http_config: HttpConfig | None = Field(
        default=None, json_schema_extra={"allow_types": [NodeType.HTTP]}
    )
