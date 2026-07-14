from enum import Enum


class StreamEventCustomToolUseType(str, Enum):
    CUSTOM_TOOL_USE = "custom_tool_use"

    def __str__(self) -> str:
        return str(self.value)
