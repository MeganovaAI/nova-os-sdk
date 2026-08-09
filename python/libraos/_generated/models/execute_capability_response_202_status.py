from enum import Enum


class ExecuteCapabilityResponse202Status(str, Enum):
    AWAITING_APPROVAL = "awaiting_approval"

    def __str__(self) -> str:
        return str(self.value)
