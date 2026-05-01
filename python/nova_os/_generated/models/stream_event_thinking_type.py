from enum import Enum


class StreamEventThinkingType(str, Enum):
    THINKING = "thinking"

    def __str__(self) -> str:
        return str(self.value)
