from enum import Enum


class NativeChatResultGrounding(str, Enum):
    DEGRADED = "degraded"
    GROUNDED = "grounded"
    UNGROUNDED_NO_CHUNKS = "ungrounded_no_chunks"
    UNGROUNDED_REFUSAL = "ungrounded_refusal"

    def __str__(self) -> str:
        return str(self.value)
