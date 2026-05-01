from enum import Enum


class StreamEventDoneType(str, Enum):
    DONE = "done"

    def __str__(self) -> str:
        return str(self.value)
