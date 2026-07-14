from enum import Enum


class ListFilesRecursive(str, Enum):
    TRUE = "true"
    VALUE_0 = "1"

    def __str__(self) -> str:
        return str(self.value)
