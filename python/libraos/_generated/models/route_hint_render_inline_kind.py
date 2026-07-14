from enum import Enum


class RouteHintRenderInlineKind(str, Enum):
    RENDER_INLINE = "render_inline"

    def __str__(self) -> str:
        return str(self.value)
