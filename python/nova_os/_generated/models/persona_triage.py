from enum import Enum


class PersonaTriage(str, Enum):
    ALWAYS_BRAIN = "always_brain"
    CONDITIONAL = "conditional"
    NEVER_BRAIN = "never_brain"

    def __str__(self) -> str:
        return str(self.value)
