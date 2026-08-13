from enum import Enum


class EvalCaseExpectedBehavior(str, Enum):
    ABSTAIN = "abstain"
    ANSWER = "answer"

    def __str__(self) -> str:
        return str(self.value)
