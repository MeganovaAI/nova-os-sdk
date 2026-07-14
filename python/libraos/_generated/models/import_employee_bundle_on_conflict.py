from enum import Enum


class ImportEmployeeBundleOnConflict(str, Enum):
    ERROR = "error"
    OVERWRITE = "overwrite"
    SKIP = "skip"

    def __str__(self) -> str:
        return str(self.value)
