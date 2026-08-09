from enum import Enum


class ExecutionReceiptOutcome(str, Enum):
    FAILED = "failed"
    SUCCEEDED = "succeeded"
    UNKNOWN = "unknown"

    def __str__(self) -> str:
        return str(self.value)
