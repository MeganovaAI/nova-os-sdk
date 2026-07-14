from enum import Enum


class StreamEventRouteHintType(str, Enum):
    ROUTE_HINT = "route_hint"

    def __str__(self) -> str:
        return str(self.value)
