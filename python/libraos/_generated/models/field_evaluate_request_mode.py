from enum import Enum


class FieldEvaluateRequestMode(str, Enum):
    VALUE_0 = ""
    WRITE = "write"

    def __str__(self) -> str:
        return str(self.value)
