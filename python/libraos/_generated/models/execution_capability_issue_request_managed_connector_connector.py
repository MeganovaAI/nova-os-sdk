from enum import Enum


class ExecutionCapabilityIssueRequestManagedConnectorConnector(str, Enum):
    SLACK = "slack"

    def __str__(self) -> str:
        return str(self.value)
