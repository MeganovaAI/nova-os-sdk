from enum import Enum


class MemoryLogScope(str, Enum):
    CORPORATE = "corporate"
    PERSONAL = "personal"

    def __str__(self) -> str:
        return str(self.value)
