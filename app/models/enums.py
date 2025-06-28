from enum import Enum, auto


class ModelType(Enum):
    OpenAI = auto()
    Ollama = auto()


class WorkflowType(Enum):
    Dag = auto()


class NodeType(Enum):
    Custom = auto()
    Input = auto()
    Output = auto()
    Model = auto()
    Text = auto()
    Image = auto()
    File = auto()
