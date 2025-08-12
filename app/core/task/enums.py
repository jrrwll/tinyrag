from enum import StrEnum
from typing import Self


class AsyncTaskStatus(StrEnum):
    Pending = "pending"
    Started = "started"
    Success = "success"
    Failure = "failure"


class AsyncTaskType(StrEnum):
    KnowledgeImport = "knowledge_import"

    @classmethod
    def knowledge_tasks(cls) -> list[Self]:
        return [cls.KnowledgeImport]
