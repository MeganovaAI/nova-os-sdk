from enum import Enum


class AutonomyGrantLifecycleState(str, Enum):
    EXPIRED = "expired"
    ISSUED = "issued"
    REVOKED = "revoked"
    SUPERSEDED = "superseded"
    SUSPENDED = "suspended"

    def __str__(self) -> str:
        return str(self.value)
