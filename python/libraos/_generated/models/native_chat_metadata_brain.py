from enum import Enum


class NativeChatMetadataBrain(str, Enum):
    ALWAYS = "always"
    NEVER = "never"

    def __str__(self) -> str:
        return str(self.value)
