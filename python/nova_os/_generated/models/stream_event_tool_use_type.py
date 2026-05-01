from enum import Enum


class StreamEventToolUseType(str, Enum):
    TOOL_USE = "tool_use"

    def __str__(self) -> str:
        return str(self.value)
