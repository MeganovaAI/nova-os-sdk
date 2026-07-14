from enum import Enum


class AgentType(str, Enum):
    PERSONA = "persona"
    SKILL = "skill"

    def __str__(self) -> str:
        return str(self.value)
