from enum import Enum


class WebSearchProviderAnswerRepresentation(str, Enum):
    MODEL_ANSWER = "model_answer"

    def __str__(self) -> str:
        return str(self.value)
