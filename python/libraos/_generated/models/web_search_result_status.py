from enum import Enum


class WebSearchResultStatus(str, Enum):
    BLOCKED_POLICY = "blocked_policy"
    BLOCKED_SOFT = "blocked_soft"
    BLOCKED_TARGET = "blocked_target"
    FETCH_FAILED = "fetch_failed"
    OPENED = "opened"

    def __str__(self) -> str:
        return str(self.value)
