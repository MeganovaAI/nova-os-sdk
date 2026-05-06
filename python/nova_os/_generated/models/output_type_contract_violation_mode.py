from enum import Enum


class OutputTypeContractViolationMode(str, Enum):
    ERROR = "error"
    LOG = "log"
    REPAIR = "repair"

    def __str__(self) -> str:
        return str(self.value)
