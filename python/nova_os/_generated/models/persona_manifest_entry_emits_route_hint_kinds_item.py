from enum import Enum


class PersonaManifestEntryEmitsRouteHintKindsItem(str, Enum):
    ASK_CLARIFICATION = "ask_clarification"
    NAVIGATE_TO = "navigate_to"
    RENDER_INLINE = "render_inline"

    def __str__(self) -> str:
        return str(self.value)
