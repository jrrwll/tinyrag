from enum import StrEnum


class WorkflowType(StrEnum):
    Graph = "graph"


class WorkflowStatus(StrEnum):
    Draft = "draft"


class NodeType(StrEnum):
    Start = "start"
    End = "end"
    LLM = "llm"
    Agent = "agent"
    Answer = "answer"
    HTTP = "http"
    Code = "code"
    Condition = "condition"
    DocExtract = "doc_extract"
    Classify = "classify"
    Template = "template"
