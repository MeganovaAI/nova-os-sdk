from enum import Enum


class ExecuteCapabilityResponse200Status(str, Enum):
    EXECUTED = "executed"

    def __str__(self) -> str:
        return str(self.value)
