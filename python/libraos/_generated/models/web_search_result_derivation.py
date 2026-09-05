from enum import Enum


class WebSearchResultDerivation(str, Enum):
    MODEL_DERIVED = "model_derived"
    PAGE_DERIVED = "page_derived"

    def __str__(self) -> str:
        return str(self.value)
