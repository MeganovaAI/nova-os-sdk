from enum import Enum


class ChatCompletionChoiceFinishReason(str, Enum):
    LENGTH = "length"
    STOP = "stop"
    TOOL_CALLS = "tool_calls"

    def __str__(self) -> str:
        return str(self.value)
