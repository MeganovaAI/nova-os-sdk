from enum import Enum


class ExecutionCapabilityPolicy(str, Enum):
    ALLOW = "allow"
    ASK = "ask"
    NEVER = "never"

    def __str__(self) -> str:
        return str(self.value)
