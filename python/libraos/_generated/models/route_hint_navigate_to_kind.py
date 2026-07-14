from enum import Enum


class RouteHintNavigateToKind(str, Enum):
    NAVIGATE_TO = "navigate_to"

    def __str__(self) -> str:
        return str(self.value)
