from enum import Enum


class WebSearchResultRepresentation(str, Enum):
    MODEL_ANSWER = "model_answer"
    PAGE_EXTRACT = "page_extract"
    PROVIDER_EXCERPT = "provider_excerpt"
    PROVIDER_SUMMARY = "provider_summary"
    SEARCH_SNIPPET = "search_snippet"

    def __str__(self) -> str:
        return str(self.value)
