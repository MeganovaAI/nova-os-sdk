from enum import Enum


class CitationCiteSource(str, Enum):
    DOCUMENT = "document"
    WEB = "web"

    def __str__(self) -> str:
        return str(self.value)
