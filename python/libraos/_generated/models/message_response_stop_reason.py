from enum import Enum


class MessageResponseStopReason(str, Enum):
    END_TURN = "end_turn"
    MAX_TOKENS = "max_tokens"
    STOP_SEQUENCE = "stop_sequence"
    TOOL_USE = "tool_use"

    def __str__(self) -> str:
        return str(self.value)
