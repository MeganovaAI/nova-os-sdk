from enum import Enum


class CustomToolCallbackAuthType(str, Enum):
    HMAC_SHA256 = "hmac_sha256"

    def __str__(self) -> str:
        return str(self.value)
