from enum import StrEnum


class AsyncTaskStatus(StrEnum):
    Pending = "pending"
    Started = "started"
    Success = "success"
    Failure = "failure"


class AsyncTaskType(StrEnum):
    KnowledgeImport = "knowledge_import"
