from enum import Enum


class CreateMessageXProtocol(str, Enum):
    AG_UI = "ag-ui"

    def __str__(self) -> str:
        return str(self.value)
