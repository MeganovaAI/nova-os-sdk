from enum import Enum


class AppMigrationStatus(str, Enum):
    APPLIED = "applied"
    FAILED = "failed"

    def __str__(self) -> str:
        return str(self.value)
