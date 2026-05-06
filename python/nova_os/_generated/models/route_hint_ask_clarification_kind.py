from enum import Enum


class RouteHintAskClarificationKind(str, Enum):
    ASK_CLARIFICATION = "ask_clarification"

    def __str__(self) -> str:
        return str(self.value)
