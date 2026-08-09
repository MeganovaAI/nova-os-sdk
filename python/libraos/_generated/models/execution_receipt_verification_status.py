from enum import Enum


class ExecutionReceiptVerificationStatus(str, Enum):
    CONTRADICTED = "contradicted"
    UNVERIFIED = "unverified"
    VERIFIED = "verified"

    def __str__(self) -> str:
        return str(self.value)
