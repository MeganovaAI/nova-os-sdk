from enum import Enum


class HookEvent(str, Enum):
    ERROR = "Error"
    POSTINFERENCE = "PostInference"
    POSTTOOLUSE = "PostToolUse"
    PREINFERENCE = "PreInference"
    PRETOOLUSE = "PreToolUse"
    SESSIONEND = "SessionEnd"
    SESSIONSTART = "SessionStart"
    STOP = "Stop"
    USERPROMPTSUBMIT = "UserPromptSubmit"

    def __str__(self) -> str:
        return str(self.value)
