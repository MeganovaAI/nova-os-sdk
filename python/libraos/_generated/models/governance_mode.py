from enum import Enum


class GovernanceMode(str, Enum):
    BROKERED = "brokered"
    DESK_MANAGED = "desk_managed"
    EXTERNAL = "external"

    def __str__(self) -> str:
        return str(self.value)
