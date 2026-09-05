from enum import Enum


class CreateKnowledgeCollectionBodyAccessLevel(str, Enum):
    CORPORATE = "corporate"
    PERSONAL = "personal"
    PRIVATE = "private"
    PUBLIC = "public"

    def __str__(self) -> str:
        return str(self.value)
