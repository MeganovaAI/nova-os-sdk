from enum import Enum


class AgentVisibility(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"
    VALUE_0 = ""

    def __str__(self) -> str:
        return str(self.value)
