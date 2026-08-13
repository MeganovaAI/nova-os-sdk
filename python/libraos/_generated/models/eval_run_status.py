from enum import Enum


class EvalRunStatus(str, Enum):
    COMPLETED = "completed"
    RUNNING = "running"

    def __str__(self) -> str:
        return str(self.value)
