from enum import Enum


class ToolUseBlockType(str, Enum):
    TOOL_USE = "tool_use"

    def __str__(self) -> str:
        return str(self.value)
