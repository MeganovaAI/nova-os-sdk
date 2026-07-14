from enum import Enum


class MessageResponseType(str, Enum):
    MESSAGE = "message"

    def __str__(self) -> str:
        return str(self.value)
