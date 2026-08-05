from enum import Enum


class ListActionsStatus(str, Enum):
    APPROVED = "approved"
    EXECUTED = "executed"
    FAILED = "failed"
    PENDING = "pending"
    REJECTED = "rejected"

    def __str__(self) -> str:
        return str(self.value)
