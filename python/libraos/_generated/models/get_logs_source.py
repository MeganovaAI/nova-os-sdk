from enum import Enum


class GetLogsSource(str, Enum):
    REQUESTS = "requests"
    SERVER = "server"

    def __str__(self) -> str:
        return str(self.value)
