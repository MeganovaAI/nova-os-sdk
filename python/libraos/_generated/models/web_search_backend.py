from enum import Enum


class WebSearchBackend(str, Enum):
    AUTO = "auto"
    BRAVE = "brave"
    EXA = "exa"
    MEGANOVA = "meganova"
    SEARXNG = "searxng"
    TAVILY = "tavily"

    def __str__(self) -> str:
        return str(self.value)
