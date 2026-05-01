from enum import Enum


class ToolDefinitionType(str, Enum):
    BASH_20250124 = "bash_20250124"
    CUSTOM = "custom"
    TEXT_EDITOR_20250124 = "text_editor_20250124"
    WEB_SEARCH_20250305 = "web_search_20250305"

    def __str__(self) -> str:
        return str(self.value)
