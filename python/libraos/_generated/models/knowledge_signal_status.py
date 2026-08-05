from enum import Enum


class KnowledgeSignalStatus(str, Enum):
    ELIGIBLE = "eligible"
    PENDING = "pending"
    PROMOTED = "promoted"
    QUARANTINED = "quarantined"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"

    def __str__(self) -> str:
        return str(self.value)
