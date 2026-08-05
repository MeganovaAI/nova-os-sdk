from enum import Enum


class FeatureStatusState(str, Enum):
    DEGRADED = "degraded"
    OFF = "off"
    ON = "on"

    def __str__(self) -> str:
        return str(self.value)
