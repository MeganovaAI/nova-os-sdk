from enum import Enum


class ExecutionCapabilityIssueRequestGovernanceMode(str, Enum):
    BROKERED = "brokered"
    DESK_MANAGED = "desk_managed"

    def __str__(self) -> str:
        return str(self.value)
