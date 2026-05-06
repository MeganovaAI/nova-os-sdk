from enum import Enum


class IngestKnowledgeResponse201Status(str, Enum):
    INGESTED = "ingested"

    def __str__(self) -> str:
        return str(self.value)
