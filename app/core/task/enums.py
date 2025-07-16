from enum import StrEnum


class AsyncTaskStatus(StrEnum):
    Pending = "pending"
    Started = "started"
    Success = "success"
    Failure = "failure"

