from enum import StrEnum


class WorkflowType(StrEnum):
    Graph = "graph"


class NodeType(StrEnum):
    Start = "start"
    End = "end"
    LLM = "llm"
    Agent = "agent"
    Answer = "answer"
    HTTP = "http"
    TOOL = "tool"
