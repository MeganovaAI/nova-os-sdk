from enum import Enum


class FieldTier(str, Enum):
    ALL = "all"
    NONE = "none"
    NON_SENSITIVE = "non-sensitive"

    def __str__(self) -> str:
        return str(self.value)
