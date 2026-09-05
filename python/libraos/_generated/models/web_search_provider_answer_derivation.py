from enum import Enum


class WebSearchProviderAnswerDerivation(str, Enum):
    MODEL_DERIVED = "model_derived"

    def __str__(self) -> str:
        return str(self.value)
