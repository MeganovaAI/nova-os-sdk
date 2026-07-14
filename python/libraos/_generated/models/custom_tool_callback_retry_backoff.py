from enum import Enum


class CustomToolCallbackRetryBackoff(str, Enum):
    EXPONENTIAL = "exponential"
    FIXED = "fixed"
    LINEAR = "linear"

    def __str__(self) -> str:
        return str(self.value)
