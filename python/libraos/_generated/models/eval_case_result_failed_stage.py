from enum import Enum


class EvalCaseResultFailedStage(str, Enum):
    ABSTENTION = "abstention"
    ACCESS = "access"
    ANSWER = "answer"
    CITATION = "citation"
    RETRIEVAL = "retrieval"

    def __str__(self) -> str:
        return str(self.value)
