from enum import Enum


class WebSearchRequestFetch(str, Enum):
    CONTENT = "content"
    NONE = "none"
    SNIPPETS = "snippets"

    def __str__(self) -> str:
        return str(self.value)
