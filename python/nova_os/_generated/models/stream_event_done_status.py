from enum import Enum


class StreamEventDoneStatus(str, Enum):
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    FAILED = "failed"

    def __str__(self) -> str:
        return str(self.value)
