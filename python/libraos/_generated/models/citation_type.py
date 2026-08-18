from enum import Enum


class CitationType(str, Enum):
    CHAR_LOCATION = "char_location"
    CONTENT_BLOCK_LOCATION = "content_block_location"
    PAGE_LOCATION = "page_location"
    WEB = "web"

    def __str__(self) -> str:
        return str(self.value)
